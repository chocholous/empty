#!/bin/bash
# Knowledge Base Search Tool
# Usage: ./search.sh <query> [--section guides|skills|graph|sources]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KB_DIR="$(dirname "$SCRIPT_DIR")"

query="${1:-}"
section="${2:-}"

if [ -z "$query" ]; then
    echo "Usage: $0 <query> [--section guides|skills|graph|sources]"
    echo ""
    echo "Examples:"
    echo "  $0 'azure devops'"
    echo "  $0 'MCP' --section guides"
    echo "  $0 'SharePoint' --section skills"
    echo ""
    echo "Sections: guides, skills, graph, sources, all (default)"
    exit 1
fi

search_dir="$KB_DIR"
if [ "$section" = "--section" ] && [ -n "${3:-}" ]; then
    search_dir="$KB_DIR/$3"
fi

echo "=== Knowledge Base Search: '$query' ==="
echo ""

# Search markdown files
echo "--- Content Matches ---"
grep -rn --include="*.md" -i "$query" "$search_dir" 2>/dev/null | while IFS= read -r line; do
    file=$(echo "$line" | cut -d: -f1 | sed "s|$KB_DIR/||")
    linenum=$(echo "$line" | cut -d: -f2)
    content=$(echo "$line" | cut -d: -f3-)
    echo "  $file:$linenum  $content"
done

echo ""

# Search knowledge graph
echo "--- Knowledge Graph Matches ---"
if [ -f "$KB_DIR/graph/knowledge-graph.json" ]; then
    # Search in nodes
    python3 -c "
import json, sys
with open('$KB_DIR/graph/knowledge-graph.json') as f:
    data = json.load(f)
q = '${query}'.lower()
print('  Nodes:')
for node in data['nodes']:
    if q in json.dumps(node).lower():
        tags = ', '.join(node.get('tags', []))
        print(f\"    [{node['type']}] {node['name']} (tags: {tags})\")
print('  Relations:')
for edge in data['edges']:
    if q in json.dumps(edge).lower():
        print(f\"    {edge['from']} --{edge['relation']}--> {edge['to']}\")
" 2>/dev/null || echo "  (python3 required for graph search)"
fi

echo ""

# Search sources
echo "--- Source Repos ---"
if [ -f "$KB_DIR/sources/repos.json" ]; then
    python3 -c "
import json
with open('$KB_DIR/sources/repos.json') as f:
    data = json.load(f)
q = '${query}'.lower()
for src in data['sources']:
    if q in json.dumps(src).lower():
        stars = src.get('stars', 'N/A')
        quality = src.get('quality', 'N/A')
        print(f\"  [{quality}] {src['name']} ({stars} stars) - {src['description'][:80]}\")
" 2>/dev/null || echo "  (python3 required for repo search)"
fi
