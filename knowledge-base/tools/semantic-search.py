#!/usr/bin/env python3
"""
Semantic Search pro Knowledge Base (TF-IDF, zero dependencies beyond stdlib).

Oproti grep:
- Rozumí synonymům a souvisejícím pojmům (přes TF-IDF podobnost)
- Rankuje výsledky podle relevance (ne jen match/no-match)
- Hledá napříč celou KB a vrací nejlepší shody
- Podporuje multi-word dotazy a fráze

Usage:
    python3 semantic-search.py "jak postavit MCP server"
    python3 semantic-search.py "azure deployment" --top 10
    python3 semantic-search.py "multi-agent orchestration" --section skills
    python3 semantic-search.py "autentizace M365" --verbose
"""

import os
import sys
import re
import math
import json
import argparse
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
KB_DIR = SCRIPT_DIR.parent

# Czech/English stop words
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
    # Czech
    "je", "jsou", "byl", "byla", "bylo", "být", "má", "mají", "pro",
    "na", "se", "ve", "do", "ze", "od", "po", "při", "přes", "mezi",
    "nad", "pod", "před", "za", "které", "který", "která", "které",
    "jak", "co", "kde", "kdy", "ten", "ta", "to", "tyto", "tato",
    "nebo", "ale", "když", "pokud", "než", "aby", "také", "tak",
    "jen", "pouze", "více", "méně", "pak", "již", "ještě",
}

# Synonym expansion: query term -> also search for these
SYNONYMS = {
    "mcp": ["model context protocol", "fastmcp", "mcp server", "mcp tools"],
    "skill": ["skills", "skill.md", "dovednost", "schopnost"],
    "skill.md": ["skill standard", "skill format", "cross-platform"],
    "agent": ["agents", "agenti", "multi-agent", "orchestrace"],
    "azure": ["microsoft azure", "az cli", "azure devops"],
    "m365": ["microsoft 365", "office 365", "graph api", "outlook", "sharepoint", "teams"],
    "graph": ["microsoft graph", "graph api", "knowledge graph"],
    "copilot": ["github copilot", "copilot studio", "copilot chat"],
    "function calling": ["tool use", "tool calling", "function call", "tools"],
    "autentizace": ["authentication", "auth", "oauth", "entra id", "msal"],
    "deployment": ["deploy", "nasazení", "provisioning"],
    "connector": ["connectors", "konektor", "konektory"],
    "plugin": ["plugins", "extension", "extensions"],
    "orchestrace": ["orchestration", "orchestrate", "workflow"],
    "semantic kernel": ["kernel_function", "process framework"],
    "openai": ["gpt", "gpt-4", "gpt actions", "chatgpt"],
    "gemini": ["google gemini", "vertex ai", "interactions api"],
    "cursor": ["cursor ide", ".cursorrules", ".mdc"],
    "terminal": ["cli", "command line", "bash", "shell"],
    "rag": ["retrieval", "vector", "embeddings", "search"],
    "declarative": ["declarative agent", "declarative agents", "manifest"],
    # Czech → English
    "debugovat": ["debug", "debugging", "troubleshoot"],
    "nefunguje": ["troubleshoot", "error", "broken", "fix"],
    "nasadit": ["deploy", "deployment", "publish"],
    "nastavení": ["configuration", "config", "settings", "setup"],
    "oprávnění": ["permissions", "rbac", "authorization", "access"],
    "smlouva": ["contract", "contract review", "legal", "nda"],
    "tabulka": ["spreadsheet", "excel", "xlsx", "openpyxl"],
    "dokument": ["document", "docx", "word", "pdf"],
    "hledání": ["search", "find", "query", "retrieval"],
    "porovnat": ["compare", "diff", "differences", "comparison"],
    "konsolidovat": ["consolidate", "merge", "aggregate", "combine"],
    # Task-oriented
    "excel": ["xlsx", "spreadsheet", "openpyxl", "workbook"],
    "dcf": ["discounted cash flow", "valuation", "financial model"],
    "lbo": ["leveraged buyout", "private equity", "pe model"],
    "comps": ["comparable company", "trading multiples", "peer analysis"],
    "pipeline": ["pipeline review", "sales pipeline", "forecast"],
    "contract": ["contract review", "smlouva", "legal", "redline"],
    "nda": ["non-disclosure", "confidentiality", "triage nda"],
}


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words, strip non-alpha."""
    text = text.lower()
    # Keep alphanumeric, dots (for package names), hyphens
    tokens = re.findall(r'[a-z0-9][a-z0-9._-]*[a-z0-9]|[a-z0-9]+', text)
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 2]


def expand_query(query: str) -> list[str]:
    """Expand query with synonyms."""
    tokens = tokenize(query)
    expanded = set(tokens)
    query_lower = query.lower()

    for key, syns in SYNONYMS.items():
        if key in query_lower or any(s in query_lower for s in syns):
            expanded.update(tokenize(key))
            for s in syns:
                expanded.update(tokenize(s))

    return list(expanded)


class Document:
    def __init__(self, path: str, title: str, section: str, content: str):
        self.path = path
        self.title = title
        self.section = section
        self.content = content
        self.tokens = tokenize(content)
        self.tf = Counter(self.tokens)
        # Normalize TF
        max_tf = max(self.tf.values()) if self.tf else 1
        self.tf_norm = {t: c / max_tf for t, c in self.tf.items()}


class TFIDFIndex:
    def __init__(self):
        self.documents: list[Document] = []
        self.df: Counter = Counter()  # document frequency
        self.N: int = 0

    def add_document(self, doc: Document):
        self.documents.append(doc)
        unique_tokens = set(doc.tokens)
        for token in unique_tokens:
            self.df[token] += 1
        self.N += 1

    def idf(self, term: str) -> float:
        if self.df[term] == 0:
            return 0
        return math.log(1 + self.N / self.df[term])

    def search(self, query: str, top_k: int = 5, section: str = None) -> list[tuple[Document, float, list[str]]]:
        """Search and return (doc, score, matched_terms) tuples."""
        query_tokens = expand_query(query)
        if not query_tokens:
            return []

        results = []
        for doc in self.documents:
            if section and doc.section != section:
                continue

            score = 0.0
            matched = []
            for qt in query_tokens:
                if qt in doc.tf_norm:
                    tfidf = doc.tf_norm[qt] * self.idf(qt)
                    score += tfidf
                    matched.append(qt)
                # Partial matching for compound terms
                elif len(qt) > 3:
                    for dt in doc.tf_norm:
                        if qt in dt or dt in qt:
                            tfidf = doc.tf_norm[dt] * self.idf(dt) * 0.5
                            score += tfidf
                            if dt not in matched:
                                matched.append(dt)

            # Boost: more matched terms = higher relevance
            if matched:
                coverage = len(matched) / len(query_tokens)
                score *= (1 + coverage)

            # Boost title matches
            title_tokens = set(tokenize(doc.title))
            title_overlap = len(set(query_tokens) & title_tokens)
            if title_overlap:
                score *= (1 + title_overlap * 0.5)

            if score > 0:
                results.append((doc, score, matched))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


def load_kb(section_filter: str = None) -> TFIDFIndex:
    """Load knowledge base into TF-IDF index."""
    index = TFIDFIndex()

    # Load guides and skills (markdown files)
    for subdir in ["guides", "skills"]:
        if section_filter and subdir != section_filter:
            continue
        dirpath = KB_DIR / subdir
        if not dirpath.exists():
            continue
        for md_file in sorted(dirpath.glob("*.md")):
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            # Extract title from first # heading
            title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
            title = title_match.group(1) if title_match else md_file.stem

            # Split into sections for finer granularity
            sections = re.split(r'\n##\s+', content)
            for i, sec in enumerate(sections):
                if i == 0:
                    sec_title = title
                else:
                    sec_title_match = re.match(r'(.+?)(?:\n|$)', sec)
                    sec_title = f"{title} → {sec_title_match.group(1)}" if sec_title_match else title

                doc = Document(
                    path=str(md_file.relative_to(KB_DIR)),
                    title=sec_title,
                    section=subdir,
                    content=sec
                )
                if len(doc.tokens) > 5:  # Skip tiny sections
                    index.add_document(doc)

    # Load knowledge graph as searchable doc
    if not section_filter or section_filter == "graph":
        graph_path = KB_DIR / "graph" / "knowledge-graph.json"
        if graph_path.exists():
            graph_data = json.loads(graph_path.read_text())
            for node in graph_data.get("nodes", []):
                content = json.dumps(node, ensure_ascii=False)
                doc = Document(
                    path="graph/knowledge-graph.json",
                    title=f"[{node.get('type', '?')}] {node.get('name', node['id'])}",
                    section="graph",
                    content=content
                )
                index.add_document(doc)

    # Load catalog (primary source for skill discovery)
    if not section_filter or section_filter in ("catalog", "sources"):
        catalog_path = KB_DIR / "catalog.json"
        if catalog_path.exists():
            catalog = json.loads(catalog_path.read_text())
            for entry in catalog.get("entries", []):
                content_parts = [
                    entry.get("name", ""),
                    entry.get("description", ""),
                    entry.get("title", ""),
                    " ".join(entry.get("tags", [])),
                    " ".join(entry.get("triggers", [])),
                    " ".join(entry.get("skills", [])),
                    " ".join(entry.get("commands", [])),
                    " ".join(entry.get("connectors", [])),
                    entry.get("repo", ""),
                ]
                content = " ".join(content_parts)
                etype = entry.get("type", "skill")
                name = entry.get("title", entry.get("name", "?"))
                doc = Document(
                    path=entry.get("path", ""),
                    title=f"[{etype}] {name}",
                    section="catalog",
                    content=content
                )
                if len(doc.tokens) > 3:
                    index.add_document(doc)

    # Load source extracts (lighter indexing - just READMEs and SKILLs)
    if not section_filter or section_filter == "sources":
        input_dir = KB_DIR / "graphrag" / "input"
        if input_dir.exists():
            for txt_file in sorted(input_dir.glob("*__README.md.txt")):
                content = txt_file.read_text(encoding="utf-8", errors="ignore")[:5000]
                repo_name = txt_file.name.split("__")[0]
                doc = Document(
                    path=f"sources/{repo_name}/README.md",
                    title=f"[source] {repo_name}",
                    section="sources",
                    content=content
                )
                index.add_document(doc)

            for txt_file in sorted(input_dir.glob("*__*SKILL.md.txt")):
                content = txt_file.read_text(encoding="utf-8", errors="ignore")[:3000]
                parts = txt_file.name.replace(".txt", "").split("__")
                repo_name = parts[0]
                skill_path = "/".join(parts[1:])
                doc = Document(
                    path=f"sources/{repo_name}/{skill_path}",
                    title=f"[skill] {repo_name}/{skill_path}",
                    section="sources",
                    content=content
                )
                index.add_document(doc)

    return index


def format_snippet(content: str, matched_terms: list[str], max_len: int = 200) -> str:
    """Extract best matching snippet from content."""
    lines = content.split('\n')
    best_line = ""
    best_score = 0

    for line in lines:
        line_lower = line.lower()
        score = sum(1 for t in matched_terms if t in line_lower)
        if score > best_score and len(line.strip()) > 20:
            best_score = score
            best_line = line.strip()

    if not best_line and lines:
        # Fallback to first non-empty line
        for line in lines:
            if len(line.strip()) > 10:
                best_line = line.strip()
                break

    if len(best_line) > max_len:
        best_line = best_line[:max_len] + "..."

    # Highlight matched terms
    for term in matched_terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        best_line = pattern.sub(f"\033[1;33m{term}\033[0m", best_line)

    return best_line


def main():
    parser = argparse.ArgumentParser(description="Semantic search v Knowledge Base (TF-IDF)")
    parser.add_argument("query", help="Hledaný dotaz (přirozený jazyk)")
    parser.add_argument("--top", type=int, default=5, help="Počet výsledků (default: 5)")
    parser.add_argument("--section", choices=["guides", "skills", "graph", "catalog", "sources"],
                       help="Omezit na sekci")
    parser.add_argument("--verbose", "-v", action="store_true", help="Podrobný výstup")
    parser.add_argument("--json", action="store_true", help="JSON výstup")
    args = parser.parse_args()

    # Build index
    index = load_kb(args.section)

    # Search
    results = index.search(args.query, top_k=args.top, section=args.section)

    if args.json:
        output = []
        for doc, score, matched in results:
            output.append({
                "path": doc.path,
                "title": doc.title,
                "section": doc.section,
                "score": round(score, 4),
                "matched_terms": matched,
                "snippet": format_snippet(doc.content, matched, 300).replace("\033[1;33m", "").replace("\033[0m", "")
            })
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # Pretty print
    expanded = expand_query(args.query)
    print(f"\n\033[1m=== Semantic Search: '{args.query}' ===\033[0m")
    print(f"Expanded terms: {', '.join(expanded[:15])}")
    print(f"Index: {index.N} documents, {len(index.df)} unique terms")
    print()

    if not results:
        print("  Žádné výsledky. Zkuste jiná klíčová slova.")
        return

    # Low-score warning
    top_score = results[0][1] if results else 0
    if top_score < 3.0:
        print(f"  \033[33m⚠ Nízká relevance (top score {top_score:.2f}). Výsledky nemusí odpovídat dotazu.\033[0m")
        print(f"  \033[33m  Zkuste specifičtější klíčová slova nebo jiný jazyk (CZ/EN).\033[0m\n")

    for i, (doc, score, matched) in enumerate(results, 1):
        section_colors = {"guides": "34", "skills": "35", "graph": "36", "sources": "32"}
        color = section_colors.get(doc.section, "37")

        print(f"  \033[1m{i}. [{doc.section}]\033[0m \033[{color}m{doc.title}\033[0m")
        print(f"     📄 {doc.path}")
        print(f"     📊 Score: {score:.3f} | Matched: {', '.join(matched[:8])}")

        snippet = format_snippet(doc.content, matched)
        if snippet:
            print(f"     💬 {snippet}")
        print()

    if args.verbose:
        print("--- Statistiky ---")
        print(f"  Dokumenty v indexu: {index.N}")
        print(f"  Unikátní termy: {len(index.df)}")
        print(f"  Top IDF termy v dotazu:")
        for t in sorted(expanded, key=lambda x: index.idf(x), reverse=True)[:10]:
            print(f"    {t}: IDF={index.idf(t):.3f}, DF={index.df[t]}")


if __name__ == "__main__":
    main()
