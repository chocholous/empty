#!/usr/bin/env python3
"""
Discovery Tool pro Knowledge Base.

Odpovídá na otázky typu:
- "Jaká témata pokrývá KB?"
- "Co všechno tu je o Azure?"
- "Které platformy podporují MCP?"
- "Jaké skills existují?"
- "Jak spolu souvisí Copilot Studio a Semantic Kernel?"

Automaticky extrahuje témata, buduje topic index a odpovídá na discovery dotazy.

Usage:
    python3 discover.py topics                    # Seznam všech témat
    python3 discover.py topics --min-docs 3       # Témata s 3+ dokumenty
    python3 discover.py related "MCP"             # Příbuzná témata k MCP
    python3 discover.py graph "copilot-studio"    # Vztahy v knowledge graphu
    python3 discover.py coverage                  # Co KB pokrývá (overview)
    python3 discover.py gaps                      # Co KB chybí (analýza mezer)
"""

import os
import sys
import re
import json
import argparse
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
KB_DIR = SCRIPT_DIR.parent


def extract_topics_from_markdown(filepath: Path) -> dict:
    """Extract topics, headings, code languages, and key terms from a markdown file."""
    content = filepath.read_text(encoding="utf-8", errors="ignore")

    # Extract headings
    headings = re.findall(r'^#{1,3}\s+(.+)', content, re.MULTILINE)

    # Extract code block languages
    code_langs = re.findall(r'```(\w+)', content)

    # Extract bold terms (likely important concepts)
    bold_terms = re.findall(r'\*\*([^*]+)\*\*', content)

    # Extract table of key terms (from | ... | patterns)
    table_terms = re.findall(r'\|\s*\*\*([^|*]+)\*\*\s*\|', content)

    # Extract links to other KB files
    internal_links = re.findall(r'\[([^\]]+)\]\(knowledge-base/([^)]+)\)', content)
    internal_links += re.findall(r'\[([^\]]+)\]\(([^)]*\.md)\)', content)

    # Extract URLs
    urls = re.findall(r'https?://[^\s)]+', content)
    github_repos = [u for u in urls if 'github.com' in u]

    # Extract package names
    packages = re.findall(r'`(@[a-z0-9/-]+|[a-z]+-[a-z]+-[a-z]+)`', content)

    return {
        "file": str(filepath.relative_to(KB_DIR)),
        "headings": headings,
        "code_languages": list(set(code_langs)),
        "key_terms": list(set(bold_terms[:30])),
        "table_terms": list(set(table_terms)),
        "internal_links": internal_links,
        "github_repos": github_repos[:10],
        "packages": list(set(packages[:15])),
        "line_count": content.count('\n'),
    }


def build_topic_index() -> dict:
    """Build comprehensive topic index from KB."""
    topics = defaultdict(lambda: {"docs": [], "count": 0, "related": set()})

    all_docs = []
    for subdir in ["guides", "skills"]:
        dirpath = KB_DIR / subdir
        if not dirpath.exists():
            continue
        for md_file in sorted(dirpath.glob("*.md")):
            info = extract_topics_from_markdown(md_file)
            info["section"] = subdir
            all_docs.append(info)

            # Index headings as topics
            for heading in info["headings"]:
                topic = heading.strip().lower()
                topics[topic]["docs"].append(info["file"])
                topics[topic]["count"] += 1

            # Index bold terms
            for term in info["key_terms"]:
                topic = term.strip().lower()
                if len(topic) > 2 and len(topic) < 60:
                    topics[topic]["docs"].append(info["file"])
                    topics[topic]["count"] += 1

    # Build relationships between topics (co-occurrence in same doc)
    for doc in all_docs:
        doc_topics = set()
        for heading in doc["headings"]:
            doc_topics.add(heading.strip().lower())
        for term in doc["key_terms"]:
            doc_topics.add(term.strip().lower())

        for t in doc_topics:
            if t in topics:
                topics[t]["related"].update(doc_topics - {t})

    # Convert sets to lists for JSON serialization
    for t in topics:
        topics[t]["related"] = sorted(topics[t]["related"])[:10]
        topics[t]["docs"] = sorted(set(topics[t]["docs"]))

    return dict(topics), all_docs


def load_graph() -> dict:
    """Load knowledge graph."""
    graph_path = KB_DIR / "graph" / "knowledge-graph.json"
    if graph_path.exists():
        return json.loads(graph_path.read_text())
    return {"nodes": [], "edges": []}


def cmd_topics(args):
    """List all discovered topics."""
    topics, _ = build_topic_index()

    # Filter and sort
    filtered = {k: v for k, v in topics.items()
                if v["count"] >= args.min_docs and len(k) > 2}
    sorted_topics = sorted(filtered.items(), key=lambda x: x[1]["count"], reverse=True)

    if args.json:
        print(json.dumps([{"topic": k, **v} for k, v in sorted_topics[:args.top]],
                         ensure_ascii=False, indent=2, default=list))
        return

    print(f"\n\033[1m=== Discovered Topics ({len(sorted_topics)} with {args.min_docs}+ docs) ===\033[0m\n")
    for i, (topic, info) in enumerate(sorted_topics[:args.top], 1):
        docs_str = ", ".join(info["docs"][:3])
        if len(info["docs"]) > 3:
            docs_str += f" +{len(info['docs'])-3}"
        print(f"  {i:2}. \033[1m{topic}\033[0m ({info['count']} mentions)")
        print(f"      📄 {docs_str}")
        if info["related"][:5]:
            print(f"      🔗 Related: {', '.join(info['related'][:5])}")
        print()


def cmd_related(args):
    """Find topics related to a given term."""
    topics, all_docs = build_topic_index()
    query = args.term.lower()

    # Direct match
    direct = []
    partial = []
    for topic, info in topics.items():
        if query == topic:
            direct.append((topic, info))
        elif query in topic or topic in query:
            partial.append((topic, info))

    # Related via co-occurrence
    related_topics = set()
    for topic, info in topics.items():
        if query in topic:
            related_topics.update(info["related"])

    if args.json:
        print(json.dumps({
            "query": query,
            "direct_matches": [{"topic": t, **v} for t, v in direct],
            "partial_matches": [{"topic": t, **v} for t, v in partial[:10]],
            "related_topics": sorted(related_topics)[:20]
        }, ensure_ascii=False, indent=2, default=list))
        return

    print(f"\n\033[1m=== Related to '{args.term}' ===\033[0m\n")

    if direct:
        print("  \033[1;32mDirect matches:\033[0m")
        for topic, info in direct:
            print(f"    • {topic} ({info['count']} mentions in {', '.join(info['docs'][:3])})")

    if partial:
        print(f"\n  \033[1;34mPartial matches ({len(partial)}):\033[0m")
        for topic, info in partial[:10]:
            print(f"    • {topic}")

    if related_topics:
        print(f"\n  \033[1;35mRelated topics ({len(related_topics)}):\033[0m")
        for rt in sorted(related_topics)[:20]:
            print(f"    • {rt}")

    # Also search knowledge graph
    graph = load_graph()
    graph_matches = []
    for node in graph.get("nodes", []):
        node_str = json.dumps(node).lower()
        if query in node_str:
            graph_matches.append(node)

    if graph_matches:
        print(f"\n  \033[1;36mKnowledge Graph nodes ({len(graph_matches)}):\033[0m")
        for node in graph_matches:
            tags = ", ".join(node.get("tags", []))
            print(f"    • [{node['type']}] {node['name']} (tags: {tags})")


def cmd_graph(args):
    """Explore knowledge graph relationships."""
    graph = load_graph()
    query = args.node.lower()

    # Find node
    target_node = None
    for node in graph.get("nodes", []):
        if query in node["id"].lower() or query in node.get("name", "").lower():
            target_node = node
            break

    if not target_node and args.json:
        print(json.dumps({"error": f"Node '{args.node}' not found"}, ensure_ascii=False))
        return
    elif not target_node:
        print(f"\n  Node '{args.node}' nenalezen. Dostupné nodes:")
        for node in graph.get("nodes", []):
            print(f"    • {node['id']} ({node.get('name', '')})")
        return

    # Find edges
    outgoing = [e for e in graph.get("edges", []) if e["from"] == target_node["id"]]
    incoming = [e for e in graph.get("edges", []) if e["to"] == target_node["id"]]

    if args.json:
        print(json.dumps({
            "node": target_node,
            "outgoing": outgoing,
            "incoming": incoming
        }, ensure_ascii=False, indent=2))
        return

    print(f"\n\033[1m=== Knowledge Graph: {target_node['name']} ===\033[0m\n")
    print(f"  Type: {target_node['type']}")
    print(f"  Tags: {', '.join(target_node.get('tags', []))}")
    for key, val in target_node.items():
        if key not in ("id", "type", "name", "tags"):
            print(f"  {key}: {val}")

    if outgoing:
        print(f"\n  \033[1;32m→ Outgoing ({len(outgoing)}):\033[0m")
        for e in outgoing:
            # Find target node name
            tgt = next((n["name"] for n in graph["nodes"] if n["id"] == e["to"]), e["to"])
            print(f"    → {e['relation']} → {tgt}")

    if incoming:
        print(f"\n  \033[1;34m← Incoming ({len(incoming)}):\033[0m")
        for e in incoming:
            src = next((n["name"] for n in graph["nodes"] if n["id"] == e["from"]), e["from"])
            print(f"    ← {src} ← {e['relation']}")


def cmd_coverage(args):
    """Show what the KB covers (overview/discovery)."""
    _, all_docs = build_topic_index()
    graph = load_graph()

    # Aggregate by section
    by_section = defaultdict(list)
    for doc in all_docs:
        by_section[doc["section"]].append(doc)

    # Aggregate code languages
    all_langs = Counter()
    all_packages = Counter()
    total_lines = 0

    for doc in all_docs:
        for lang in doc["code_languages"]:
            all_langs[lang] += 1
        for pkg in doc["packages"]:
            all_packages[pkg] += 1
        total_lines += doc["line_count"]

    if args.json:
        output = {
            "sections": {k: len(v) for k, v in by_section.items()},
            "total_docs": len(all_docs),
            "total_lines": total_lines,
            "code_languages": dict(all_langs.most_common(15)),
            "top_packages": dict(all_packages.most_common(20)),
            "graph_nodes": len(graph.get("nodes", [])),
            "graph_edges": len(graph.get("edges", [])),
            "platforms": [n["name"] for n in graph.get("nodes", []) if n.get("type") == "platform"],
            "services": [n["name"] for n in graph.get("nodes", []) if n.get("type") == "service"],
            "mcp_servers": [n["name"] for n in graph.get("nodes", []) if n.get("type") == "mcp-server"],
            "skills_repos": [n["name"] for n in graph.get("nodes", []) if n.get("type") == "skills-repo"],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print(f"\n\033[1m=== Knowledge Base Coverage ===\033[0m\n")

    print(f"  📊 \033[1m{len(all_docs)} dokumentů\033[0m, {total_lines:,} řádků\n")

    # Sections
    print("  \033[1mSekce:\033[0m")
    for section, docs in sorted(by_section.items()):
        print(f"    📁 {section}/ ({len(docs)} souborů)")
        for doc in docs:
            headings_preview = " | ".join(doc["headings"][:3])
            print(f"       • {doc['file']} — {headings_preview}")

    # Graph
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    print(f"\n  \033[1mKnowledge Graph:\033[0m {len(nodes)} nodes, {len(edges)} edges")

    by_type = defaultdict(list)
    for n in nodes:
        by_type[n.get("type", "?")].append(n["name"])

    for ntype, names in sorted(by_type.items()):
        print(f"    [{ntype}] ({len(names)}): {', '.join(names[:5])}")
        if len(names) > 5:
            print(f"      ... +{len(names)-5} more")

    # Languages & packages
    print(f"\n  \033[1mCode examples:\033[0m {sum(all_langs.values())} bloků")
    for lang, count in all_langs.most_common(10):
        print(f"    • {lang}: {count} bloků")

    print(f"\n  \033[1mTop packages:\033[0m")
    for pkg, count in all_packages.most_common(10):
        print(f"    • {pkg} ({count}x)")


def cmd_gaps(args):
    """Analyze what might be missing from the KB."""
    topics, all_docs = build_topic_index()
    graph = load_graph()

    # Expected topics that should be covered
    expected = {
        "authentication patterns": ["oauth", "msal", "entra", "managed identity"],
        "error handling": ["error", "exception", "retry", "fallback"],
        "testing": ["test", "testing", "pytest", "jest", "unit test"],
        "security": ["security", "rbac", "permissions", "secrets"],
        "monitoring": ["monitoring", "observability", "telemetry", "logging"],
        "caching": ["cache", "caching", "redis", "prompt caching"],
        "rate limiting": ["rate limit", "throttle", "quota"],
        "cost optimization": ["cost", "pricing", "optimization", "budget"],
        "streaming": ["streaming", "sse", "websocket", "server-sent"],
        "batch processing": ["batch", "bulk", "parallel processing"],
    }

    # Check coverage
    all_content = ""
    for doc in all_docs:
        filepath = KB_DIR / doc["file"]
        if filepath.exists():
            all_content += filepath.read_text(encoding="utf-8", errors="ignore").lower()

    if args.json:
        coverage = {}
        for area, keywords in expected.items():
            mentions = sum(all_content.count(kw) for kw in keywords)
            coverage[area] = {"keywords": keywords, "mentions": mentions,
                            "status": "covered" if mentions > 5 else "weak" if mentions > 0 else "missing"}
        print(json.dumps(coverage, ensure_ascii=False, indent=2))
        return

    print(f"\n\033[1m=== Knowledge Base Gap Analysis ===\033[0m\n")

    for area, keywords in sorted(expected.items()):
        mentions = sum(all_content.count(kw) for kw in keywords)
        if mentions > 5:
            status = "\033[32m✓ Covered\033[0m"
        elif mentions > 0:
            status = "\033[33m⚠ Weak\033[0m"
        else:
            status = "\033[31m✗ Missing\033[0m"
        print(f"  {status}  {area} ({mentions} mentions)")

    # Check graph completeness
    print(f"\n  \033[1mGraph completeness:\033[0m")
    nodes_with_no_edges = []
    node_ids = {n["id"] for n in graph.get("nodes", [])}
    edge_nodes = set()
    for e in graph.get("edges", []):
        edge_nodes.add(e["from"])
        edge_nodes.add(e["to"])

    orphans = node_ids - edge_nodes
    if orphans:
        print(f"    ⚠ Orphan nodes (no edges): {', '.join(sorted(orphans))}")
    else:
        print(f"    ✓ All nodes connected")

    # Check for broken edge references
    broken = []
    for e in graph.get("edges", []):
        if e["from"] not in node_ids:
            broken.append(f"{e['from']} (in edge → {e['to']})")
        if e["to"] not in node_ids:
            broken.append(f"{e['to']} (in edge from {e['from']})")
    if broken:
        print(f"    ⚠ Broken edge references: {', '.join(broken)}")
    else:
        print(f"    ✓ All edge references valid")


def main():
    parser = argparse.ArgumentParser(description="Knowledge Base Discovery Tool")
    parser.add_argument("--json", action="store_true", help="JSON výstup")
    subparsers = parser.add_subparsers(dest="command", help="Příkaz")

    # topics
    p_topics = subparsers.add_parser("topics", help="Zobrazit všechna témata")
    p_topics.add_argument("--min-docs", type=int, default=2, help="Min. počet dokumentů (default: 2)")
    p_topics.add_argument("--top", type=int, default=30, help="Počet témat (default: 30)")
    p_topics.add_argument("--json", action="store_true", help="JSON výstup")

    # related
    p_related = subparsers.add_parser("related", help="Najít příbuzná témata")
    p_related.add_argument("term", help="Hledaný pojem")
    p_related.add_argument("--json", action="store_true", help="JSON výstup")

    # graph
    p_graph = subparsers.add_parser("graph", help="Prozkoumat knowledge graph")
    p_graph.add_argument("node", help="ID nebo název node")
    p_graph.add_argument("--json", action="store_true", help="JSON výstup")

    # coverage
    p_coverage = subparsers.add_parser("coverage", help="Přehled pokrytí KB")
    p_coverage.add_argument("--json", action="store_true", help="JSON výstup")

    # gaps
    p_gaps = subparsers.add_parser("gaps", help="Analýza mezer v KB")
    p_gaps.add_argument("--json", action="store_true", help="JSON výstup")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "topics": cmd_topics,
        "related": cmd_related,
        "graph": cmd_graph,
        "coverage": cmd_coverage,
        "gaps": cmd_gaps,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
