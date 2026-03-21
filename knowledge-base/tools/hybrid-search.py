#!/usr/bin/env python3
"""
Hybrid Search: BM25 + Embeddings + Reciprocal Rank Fusion (RRF) + Cross-Encoder Reranker.

Tři retrieval strategie v jednom:
1. BM25 — keyword matching s TF-IDF váhami (přesné termy, typo-tolerant)
2. Embeddings — sémantická podobnost (rozumí významu, cross-language)
3. RRF fusion — kombinuje oba rankingy do jednoho
4. Cross-encoder reranker (optional) — přeřadí top-K kandidáty přesným skóre

Oproti stávajícím nástrojům:
- semantic-search.py: TF-IDF only, ručně definované synonymy
- build-catalog.py --search: keyword counting, žádná sémantika
- hybrid-search.py: BM25 + neural embeddings + fusion

Usage:
    # Základní hybrid search
    python3 hybrid-search.py "jak porovnat dvě tabulky"

    # S cross-encoder rerankerem (pomalejší, přesnější)
    python3 hybrid-search.py "financial model audit" --rerank

    # Jen BM25 nebo jen embeddings
    python3 hybrid-search.py "dcf valuation" --mode bm25
    python3 hybrid-search.py "dcf valuation" --mode embedding

    # Build/rebuild index (pre-compute embeddings)
    python3 hybrid-search.py --build-index

    # JSON output
    python3 hybrid-search.py "contract review" --json --top 10
"""

import os
import sys
import re
import json
import math
import time
import pickle
import hashlib
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from typing import Optional

SCRIPT_DIR = Path(__file__).parent
KB_DIR = SCRIPT_DIR.parent
CATALOG_PATH = KB_DIR / "catalog.json"
INDEX_DIR = KB_DIR / "tools" / ".hybrid-index"

# Embedding model — small, fast, multilingual
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# RRF constant (standard value from Cormack et al. 2009)
RRF_K = 60

# Czech/English stop words (reused from semantic-search.py)
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "out", "off", "over",
    "under", "again", "further", "then", "once", "here", "there", "when",
    "where", "why", "how", "all", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "not", "only", "own", "same", "so",
    "than", "too", "very", "just", "or", "and", "but", "if", "while",
    "about", "up", "it", "its", "this", "that", "these", "those",
    "je", "jsou", "byl", "byla", "bylo", "být", "má", "mají", "pro",
    "na", "se", "ve", "do", "ze", "od", "po", "při", "přes", "mezi",
    "nad", "pod", "před", "za", "které", "který", "která",
    "jak", "co", "kde", "kdy", "ten", "ta", "to", "tyto", "tato",
    "nebo", "ale", "když", "pokud", "než", "aby", "také", "tak",
    "jen", "pouze", "více", "méně", "pak", "již", "ještě",
}


# ─────────────────────────────────────────────────────────────
# Document loading (shared across all strategies)
# ─────────────────────────────────────────────────────────────

class SearchDocument:
    """A searchable document with text and metadata."""
    __slots__ = ("doc_id", "path", "title", "section", "doc_type", "text", "tags")

    def __init__(self, doc_id: str, path: str, title: str, section: str,
                 doc_type: str, text: str, tags: list[str]):
        self.doc_id = doc_id
        self.path = path
        self.title = title
        self.section = section
        self.doc_type = doc_type
        self.text = text
        self.tags = tags


def load_documents() -> list[SearchDocument]:
    """Load all searchable documents from catalog + guides + skills."""
    docs = []

    # 1. Catalog entries (668 items — primary source)
    if CATALOG_PATH.exists():
        catalog = json.loads(CATALOG_PATH.read_text())
        for i, entry in enumerate(catalog.get("entries", [])):
            text_parts = [
                entry.get("name", ""),
                entry.get("title", ""),
                entry.get("description", ""),
                " ".join(entry.get("tags", [])),
                " ".join(entry.get("triggers", [])),
                " ".join(entry.get("skills", [])),
                " ".join(entry.get("commands", [])),
                " ".join(entry.get("connectors", [])),
                entry.get("repo", ""),
            ]
            text = " ".join(t for t in text_parts if t)

            docs.append(SearchDocument(
                doc_id=f"catalog:{i}",
                path=entry.get("path", ""),
                title=entry.get("title", entry.get("name", f"entry-{i}")),
                section="catalog",
                doc_type=entry.get("type", "skill"),
                text=text,
                tags=entry.get("tags", []),
            ))

    # 2. Guides (platform docs)
    guides_dir = KB_DIR / "guides"
    if guides_dir.exists():
        for md_file in sorted(guides_dir.glob("*.md")):
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
            title = title_match.group(1) if title_match else md_file.stem

            # Split into sections for better granularity
            sections = re.split(r'\n##\s+', content)
            for j, sec in enumerate(sections):
                if j == 0:
                    sec_title = title
                else:
                    sec_title_match = re.match(r'(.+?)(?:\n|$)', sec)
                    sec_title = f"{title} > {sec_title_match.group(1)}" if sec_title_match else title

                # Clean markdown for embedding
                clean = _clean_markdown(sec)
                if len(clean.split()) < 10:
                    continue

                docs.append(SearchDocument(
                    doc_id=f"guide:{md_file.stem}:{j}",
                    path=str(md_file.relative_to(KB_DIR)),
                    title=sec_title,
                    section="guides",
                    doc_type="guide",
                    text=clean,
                    tags=[],
                ))

    # 3. Skills docs
    skills_dir = KB_DIR / "skills"
    if skills_dir.exists():
        for md_file in sorted(skills_dir.glob("*.md")):
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
            title = title_match.group(1) if title_match else md_file.stem

            sections = re.split(r'\n##\s+', content)
            for j, sec in enumerate(sections):
                if j == 0:
                    sec_title = title
                else:
                    sec_title_match = re.match(r'(.+?)(?:\n|$)', sec)
                    sec_title = f"{title} > {sec_title_match.group(1)}" if sec_title_match else title

                clean = _clean_markdown(sec)
                if len(clean.split()) < 10:
                    continue

                docs.append(SearchDocument(
                    doc_id=f"skill:{md_file.stem}:{j}",
                    path=str(md_file.relative_to(KB_DIR)),
                    title=sec_title,
                    section="skills",
                    doc_type="skill-doc",
                    text=clean,
                    tags=[],
                ))

    # 4. Source SKILL.md extracts (from graphrag/input)
    input_dir = KB_DIR / "graphrag" / "input"
    if input_dir.exists():
        for txt_file in sorted(input_dir.glob("*SKILL.md.txt")):
            content = txt_file.read_text(encoding="utf-8", errors="ignore")[:3000]
            parts = txt_file.name.replace(".txt", "").split("__")
            repo = parts[0]
            skill_path = "/".join(parts[1:])

            docs.append(SearchDocument(
                doc_id=f"source:{txt_file.stem}",
                path=f"sources/{repo}/{skill_path}",
                title=f"{repo}/{skill_path}",
                section="sources",
                doc_type="source-skill",
                text=_clean_markdown(content),
                tags=[],
            ))

    return docs


def _clean_markdown(text: str) -> str:
    """Strip markdown formatting for cleaner embedding."""
    text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', text, flags=re.DOTALL)
    text = re.sub(r'```[\s\S]*?```', ' ', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'[#*`|>]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ─────────────────────────────────────────────────────────────
# BM25 Component
# ─────────────────────────────────────────────────────────────

def tokenize(text: str) -> list[str]:
    """Tokenize for BM25."""
    text = text.lower()
    tokens = re.findall(r'[a-z0-9][a-z0-9._-]*[a-z0-9]|[a-z0-9]+', text)
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]


class BM25Index:
    """Okapi BM25 implementation (no external deps, numpy optional)."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_ids: list[str] = []
        self.doc_lens: list[int] = []
        self.avgdl: float = 0
        self.N: int = 0
        self.tf: list[dict[str, int]] = []  # per-doc term frequencies
        self.df: Counter = Counter()  # document frequency
        self.idf: dict[str, float] = {}

    def build(self, docs: list[SearchDocument]):
        """Index all documents."""
        self.doc_ids = []
        self.tf = []
        self.doc_lens = []
        self.df = Counter()

        for doc in docs:
            tokens = tokenize(doc.text)
            tf = Counter(tokens)

            self.doc_ids.append(doc.doc_id)
            self.tf.append(tf)
            self.doc_lens.append(len(tokens))

            for term in set(tokens):
                self.df[term] += 1

        self.N = len(docs)
        self.avgdl = sum(self.doc_lens) / self.N if self.N > 0 else 1

        # Pre-compute IDF (BM25 variant)
        for term, df in self.df.items():
            self.idf[term] = math.log((self.N - df + 0.5) / (df + 0.5) + 1)

    def search(self, query: str, top_k: int = 50) -> list[tuple[str, float]]:
        """Return (doc_id, score) sorted by BM25 score."""
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores: dict[str, float] = {}
        for i in range(self.N):
            score = 0.0
            dl = self.doc_lens[i]
            tf_doc = self.tf[i]

            for qt in query_tokens:
                if qt not in tf_doc:
                    continue
                tf_val = tf_doc[qt]
                idf_val = self.idf.get(qt, 0)
                # BM25 formula
                numerator = tf_val * (self.k1 + 1)
                denominator = tf_val + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                score += idf_val * numerator / denominator

            if score > 0:
                scores[self.doc_ids[i]] = score

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]


# ─────────────────────────────────────────────────────────────
# Embedding Component
# ─────────────────────────────────────────────────────────────

class EmbeddingIndex:
    """Dense vector search using sentence-transformers."""

    def __init__(self):
        self.model = None
        self.doc_ids: list[str] = []
        self.embeddings = None  # numpy array (N, dim)

    def _load_model(self):
        if self.model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(EMBEDDING_MODEL)
        except ImportError:
            raise RuntimeError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )

    def build(self, docs: list[SearchDocument], batch_size: int = 64):
        """Compute embeddings for all documents."""
        self._load_model()
        import numpy as np

        self.doc_ids = [d.doc_id for d in docs]
        texts = [f"{d.title}. {d.text[:512]}" for d in docs]

        print(f"  Computing embeddings for {len(texts)} documents...", file=sys.stderr)
        self.embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True,  # L2-normalized for cosine via dot product
        )
        print(f"  Embeddings shape: {self.embeddings.shape}", file=sys.stderr)

    def search(self, query: str, top_k: int = 50) -> list[tuple[str, float]]:
        """Return (doc_id, cosine_similarity) sorted desc."""
        self._load_model()
        import numpy as np

        query_emb = self.model.encode(
            [query],
            normalize_embeddings=True,
        )
        # Cosine similarity = dot product (both normalized)
        scores = np.dot(self.embeddings, query_emb.T).flatten()

        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(self.doc_ids[i], float(scores[i])) for i in top_indices]

    def save(self, path: Path):
        """Save embeddings to disk."""
        import numpy as np
        path.mkdir(parents=True, exist_ok=True)
        np.save(path / "embeddings.npy", self.embeddings)
        with open(path / "doc_ids.json", "w") as f:
            json.dump(self.doc_ids, f)

    def load(self, path: Path) -> bool:
        """Load pre-computed embeddings. Returns False if not found."""
        emb_path = path / "embeddings.npy"
        ids_path = path / "doc_ids.json"
        if not emb_path.exists() or not ids_path.exists():
            return False
        import numpy as np
        self.embeddings = np.load(emb_path)
        with open(ids_path) as f:
            self.doc_ids = json.load(f)
        return True


# ─────────────────────────────────────────────────────────────
# Cross-Encoder Reranker
# ─────────────────────────────────────────────────────────────

class CrossEncoderReranker:
    """Rerank candidates using a cross-encoder model."""

    def __init__(self):
        self.model = None

    def _load_model(self):
        if self.model is not None:
            return
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(RERANKER_MODEL)
        except ImportError:
            raise RuntimeError("sentence-transformers not installed for cross-encoder.")

    def rerank(self, query: str, candidates: list[tuple[str, SearchDocument, float]],
               top_k: int = 10) -> list[tuple[str, SearchDocument, float]]:
        """Rerank (doc_id, doc, rrf_score) tuples using cross-encoder."""
        if not candidates:
            return []

        self._load_model()

        pairs = [(query, f"{doc.title}. {doc.text[:512]}") for _, doc, _ in candidates]
        scores = self.model.predict(pairs)

        reranked = []
        for i, (doc_id, doc, _) in enumerate(candidates):
            reranked.append((doc_id, doc, float(scores[i])))

        reranked.sort(key=lambda x: x[2], reverse=True)
        return reranked[:top_k]


# ─────────────────────────────────────────────────────────────
# Reciprocal Rank Fusion (RRF)
# ─────────────────────────────────────────────────────────────

def reciprocal_rank_fusion(
    rankings: list[list[tuple[str, float]]],
    k: int = RRF_K,
) -> list[tuple[str, float]]:
    """
    Combine multiple rankings using RRF.

    Each ranking is a list of (doc_id, score) sorted by score desc.
    Returns (doc_id, rrf_score) sorted desc.

    RRF(d) = Σ 1 / (k + rank_i(d))
    """
    rrf_scores: dict[str, float] = defaultdict(float)

    for ranking in rankings:
        for rank, (doc_id, _) in enumerate(ranking, start=1):
            rrf_scores[doc_id] += 1.0 / (k + rank)

    sorted_scores = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_scores


# ─────────────────────────────────────────────────────────────
# Hybrid Search Engine
# ─────────────────────────────────────────────────────────────

class HybridSearch:
    """Orchestrates BM25 + Embeddings + RRF + optional Cross-Encoder."""

    def __init__(self):
        self.docs: list[SearchDocument] = []
        self.doc_map: dict[str, SearchDocument] = {}
        self.bm25 = BM25Index()
        self.embedding_index = EmbeddingIndex()
        self.reranker: Optional[CrossEncoderReranker] = None
        self._index_hash: str = ""

    def _catalog_hash(self) -> str:
        """Hash of catalog to detect changes."""
        if CATALOG_PATH.exists():
            content = CATALOG_PATH.read_bytes()
            return hashlib.md5(content).hexdigest()[:12]
        return "no-catalog"

    def build_index(self, force: bool = False):
        """Build all indexes (BM25 + embeddings)."""
        current_hash = self._catalog_hash()
        hash_file = INDEX_DIR / "catalog_hash.txt"

        # Check if rebuild needed
        if not force and hash_file.exists():
            saved_hash = hash_file.read_text().strip()
            if saved_hash == current_hash and self.embedding_index.load(INDEX_DIR):
                print(f"  Using cached index (hash: {current_hash})", file=sys.stderr)
                self.docs = load_documents()
                self.doc_map = {d.doc_id: d for d in self.docs}
                self.bm25.build(self.docs)

                # Verify doc count matches
                if len(self.embedding_index.doc_ids) == len(self.docs):
                    return
                print("  Doc count mismatch, rebuilding...", file=sys.stderr)

        # Full rebuild
        print("Building hybrid index...", file=sys.stderr)
        t0 = time.time()

        self.docs = load_documents()
        self.doc_map = {d.doc_id: d for d in self.docs}
        print(f"  Loaded {len(self.docs)} documents", file=sys.stderr)

        # BM25
        t1 = time.time()
        self.bm25.build(self.docs)
        print(f"  BM25 index built ({time.time() - t1:.1f}s)", file=sys.stderr)

        # Embeddings
        t2 = time.time()
        self.embedding_index.build(self.docs)
        print(f"  Embedding index built ({time.time() - t2:.1f}s)", file=sys.stderr)

        # Save
        self.embedding_index.save(INDEX_DIR)
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        hash_file.write_text(current_hash)

        print(f"  Total build time: {time.time() - t0:.1f}s", file=sys.stderr)

    def search(
        self,
        query: str,
        top_k: int = 10,
        mode: str = "hybrid",
        use_reranker: bool = False,
        retrieval_k: int = 50,
    ) -> list[tuple[str, SearchDocument, float, dict]]:
        """
        Search and return (doc_id, doc, final_score, metadata) tuples.

        Modes: "hybrid", "bm25", "embedding"
        """
        if not self.docs:
            self.build_index()

        metadata_map: dict[str, dict] = defaultdict(dict)

        if mode == "bm25":
            bm25_results = self.bm25.search(query, top_k=retrieval_k)
            for doc_id, score in bm25_results:
                metadata_map[doc_id]["bm25_score"] = score
            fused = bm25_results[:top_k]
        elif mode == "embedding":
            emb_results = self.embedding_index.search(query, top_k=retrieval_k)
            for doc_id, score in emb_results:
                metadata_map[doc_id]["embedding_score"] = score
            fused = emb_results[:top_k]
        else:
            # Hybrid: BM25 + Embeddings → RRF
            bm25_results = self.bm25.search(query, top_k=retrieval_k)
            emb_results = self.embedding_index.search(query, top_k=retrieval_k)

            for doc_id, score in bm25_results:
                metadata_map[doc_id]["bm25_score"] = score
                metadata_map[doc_id]["bm25_rank"] = next(
                    r for r, (d, _) in enumerate(bm25_results, 1) if d == doc_id
                )
            for doc_id, score in emb_results:
                metadata_map[doc_id]["embedding_score"] = score
                metadata_map[doc_id]["embedding_rank"] = next(
                    r for r, (d, _) in enumerate(emb_results, 1) if d == doc_id
                )

            fused = reciprocal_rank_fusion([bm25_results, emb_results])

        # Optional cross-encoder reranking
        if use_reranker and mode != "bm25":
            candidates = [
                (doc_id, self.doc_map[doc_id], score)
                for doc_id, score in fused[:min(30, len(fused))]
                if doc_id in self.doc_map
            ]
            if self.reranker is None:
                self.reranker = CrossEncoderReranker()
            reranked = self.reranker.rerank(query, candidates, top_k=top_k)
            results = [
                (doc_id, doc, score, metadata_map.get(doc_id, {}))
                for doc_id, doc, score in reranked
            ]
            for r in results:
                r[3]["reranker_score"] = r[2]
            return results

        # Without reranker, return top-K from fusion
        results = []
        for doc_id, score in fused[:top_k]:
            if doc_id in self.doc_map:
                results.append((doc_id, self.doc_map[doc_id], score, metadata_map.get(doc_id, {})))

        return results


# ─────────────────────────────────────────────────────────────
# Output formatting
# ─────────────────────────────────────────────────────────────

def format_snippet(text: str, max_len: int = 150) -> str:
    """First meaningful portion of text."""
    text = text[:max_len * 2]
    # Find first sentence-like chunk
    sentences = re.split(r'[.!?]\s', text)
    snippet = sentences[0] if sentences else text
    if len(snippet) > max_len:
        snippet = snippet[:max_len] + "..."
    return snippet.strip()


def print_results(results, query: str, mode: str, verbose: bool = False):
    """Pretty-print search results."""
    print(f"\n\033[1m=== Hybrid Search: '{query}' (mode={mode}) ===\033[0m")
    print(f"Results: {len(results)}\n")

    if not results:
        print("  No results found. Try different keywords or language (CZ/EN).")
        return

    section_colors = {
        "catalog": "32", "guides": "34", "skills": "35", "sources": "36"
    }
    type_icons = {
        "skill": "⚡", "plugin": "🔌", "cookbook": "📖",
        "guide": "📘", "skill-doc": "📄", "source-skill": "📁"
    }

    for i, (doc_id, doc, score, meta) in enumerate(results, 1):
        color = section_colors.get(doc.section, "37")
        icon = type_icons.get(doc.doc_type, "📝")

        print(f"  \033[1m{i}.\033[0m {icon} \033[{color}m{doc.title}\033[0m")
        print(f"     Path: {doc.path}")
        print(f"     Score: {score:.4f}", end="")

        if verbose and meta:
            parts = []
            if "bm25_score" in meta:
                parts.append(f"BM25={meta['bm25_score']:.3f}")
            if "bm25_rank" in meta:
                parts.append(f"BM25r=#{meta['bm25_rank']}")
            if "embedding_score" in meta:
                parts.append(f"Emb={meta['embedding_score']:.3f}")
            if "embedding_rank" in meta:
                parts.append(f"Embr=#{meta['embedding_rank']}")
            if "reranker_score" in meta:
                parts.append(f"Rerank={meta['reranker_score']:.3f}")
            if parts:
                print(f"  ({', '.join(parts)})", end="")

        print()

        if doc.tags:
            print(f"     Tags: {', '.join(doc.tags[:6])}")

        snippet = format_snippet(doc.text)
        if snippet:
            print(f"     {snippet}")
        print()


def results_to_json(results) -> list[dict]:
    """Convert results to JSON-serializable format."""
    output = []
    for doc_id, doc, score, meta in results:
        output.append({
            "doc_id": doc_id,
            "path": doc.path,
            "title": doc.title,
            "section": doc.section,
            "type": doc.doc_type,
            "score": round(score, 5),
            "tags": doc.tags,
            "snippet": format_snippet(doc.text, 300),
            "meta": {k: round(v, 4) if isinstance(v, float) else v for k, v in meta.items()},
        })
    return output


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Hybrid Search: BM25 + Embeddings + RRF + Reranker"
    )
    parser.add_argument("query", nargs="?", help="Search query (natural language)")
    parser.add_argument("--top", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument("--mode", choices=["hybrid", "bm25", "embedding"],
                        default="hybrid", help="Search mode")
    parser.add_argument("--rerank", action="store_true",
                        help="Use cross-encoder reranker (slower, more accurate)")
    parser.add_argument("--build-index", action="store_true",
                        help="Build/rebuild embedding index")
    parser.add_argument("--force-rebuild", action="store_true",
                        help="Force index rebuild even if cached")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show scoring details")
    args = parser.parse_args()

    engine = HybridSearch()

    if args.build_index or args.force_rebuild:
        engine.build_index(force=args.force_rebuild)
        print("Index built successfully.", file=sys.stderr)
        if not args.query:
            return

    if not args.query:
        parser.error("Please provide a search query or use --build-index")

    results = engine.search(
        query=args.query,
        top_k=args.top,
        mode=args.mode,
        use_reranker=args.rerank,
    )

    if args.json:
        print(json.dumps(results_to_json(results), ensure_ascii=False, indent=2))
    else:
        print_results(results, args.query, args.mode, verbose=args.verbose)


if __name__ == "__main__":
    main()
