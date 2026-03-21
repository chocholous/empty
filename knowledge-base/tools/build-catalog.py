#!/usr/bin/env python3
"""
Build Skills Catalog — automatický index všech SKILL.md, pluginů a cookbooks.

Prochází sources/, extrahuje metadata z SKILL.md (YAML frontmatter),
plugin.json a README.md a vytváří JSON katalog pro semantic search.

Usage:
    python3 build-catalog.py                    # Build + uložit catalog.json
    python3 build-catalog.py --stats            # Jen statistiky
    python3 build-catalog.py --search "excel"   # Hledat v katalogu
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
KB_DIR = SCRIPT_DIR.parent
SOURCES_DIR = KB_DIR / "sources"
CATALOG_PATH = KB_DIR / "catalog.json"


def parse_yaml_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from SKILL.md (simplified parser, no deps)."""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    yaml_text = match.group(1)
    result = {}
    current_key = None
    current_value = []

    for line in yaml_text.split('\n'):
        # Simple key: value
        kv_match = re.match(r'^(\w[\w-]*)\s*:\s*"?(.+?)"?\s*$', line)
        if kv_match:
            if current_key and current_value:
                result[current_key] = '\n'.join(current_value)
            current_key = kv_match.group(1)
            current_value = [kv_match.group(2).strip('"').strip("'")]
        elif current_key and line.startswith('  '):
            # Continuation of multi-line value
            current_value.append(line.strip())
        elif line.strip() == '' and current_key:
            continue

    if current_key and current_value:
        result[current_key] = '\n'.join(current_value)

    return result


def extract_first_section(content: str, max_chars: int = 500) -> str:
    """Extract content after frontmatter, first meaningful section."""
    # Remove frontmatter
    content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
    # Get first section (up to second ## heading)
    sections = re.split(r'\n##\s+', content, maxsplit=2)
    text = sections[0] if sections else content
    # Clean markdown
    text = re.sub(r'```[\s\S]*?```', '', text)  # Remove code blocks
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links to text
    text = re.sub(r'[#*`|>]', '', text)  # Remove markdown chars
    text = re.sub(r'\n{2,}', '\n', text).strip()
    return text[:max_chars]


def scan_skill_files() -> list:
    """Find and parse all SKILL.md files."""
    skills = []
    for skill_path in sorted(SOURCES_DIR.rglob("SKILL.md")):
        try:
            content = skill_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        meta = parse_yaml_frontmatter(content)
        rel_path = str(skill_path.relative_to(KB_DIR))

        # Determine repo and skill path
        parts = skill_path.relative_to(SOURCES_DIR).parts
        repo = parts[0] if parts else "unknown"

        # Extract trigger phrases from description
        triggers = []
        desc = meta.get("description", "")
        trigger_match = re.findall(r'[Tt]rigger\s+(?:with\s+)?["\']([^"\']+)["\']', desc)
        triggers.extend(trigger_match)
        # Also from content
        trigger_match2 = re.findall(r'\*\*Trigger:?\*\*\s*(.+)', content)
        for t in trigger_match2:
            triggers.extend([x.strip().strip('"').strip("'") for x in t.split(',')])

        skills.append({
            "type": "skill",
            "name": meta.get("name", skill_path.parent.name),
            "description": desc[:300] if desc else extract_first_section(content, 300),
            "path": rel_path,
            "repo": repo,
            "triggers": triggers[:5],
            "tags": _extract_tags(content, meta),
        })

    return skills


def scan_plugins() -> list:
    """Find and parse all plugin.json files."""
    plugins = []
    for pj_path in sorted(SOURCES_DIR.rglob("plugin.json")):
        try:
            data = json.loads(pj_path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue

        rel_path = str(pj_path.relative_to(KB_DIR))
        parts = pj_path.relative_to(SOURCES_DIR).parts
        repo = parts[0] if parts else "unknown"

        # Find associated skills and commands
        plugin_dir = pj_path.parent.parent  # Go up from .claude-plugin/
        skill_names = []
        command_names = []

        skills_dir = plugin_dir / "skills"
        if skills_dir.exists():
            for s in skills_dir.iterdir():
                if s.is_dir():
                    skill_names.append(s.name)

        commands_dir = plugin_dir / "commands"
        if commands_dir.exists():
            for c in commands_dir.iterdir():
                if c.is_dir():
                    command_names.append(c.name)

        # Find CONNECTORS.md for MCP info
        connectors = []
        conn_path = plugin_dir / "CONNECTORS.md"
        if conn_path.exists():
            conn_content = conn_path.read_text(encoding="utf-8", errors="ignore")
            # Extract connector names from headers or bold terms
            connectors = re.findall(r'##\s+(\w[\w\s]+)', conn_content)[:10]

        plugins.append({
            "type": "plugin",
            "name": data.get("name", plugin_dir.name),
            "description": data.get("description", "")[:300],
            "version": data.get("version", ""),
            "path": rel_path,
            "repo": repo,
            "skills": skill_names,
            "commands": command_names,
            "connectors": connectors,
            "tags": _extract_tags_from_plugin(data, skill_names, command_names),
        })

    return plugins


def scan_cookbooks() -> list:
    """Find notable cookbook entries (README.md with examples)."""
    cookbooks = []

    # openai-cookbook examples
    examples_dir = SOURCES_DIR / "openai-cookbook" / "examples"
    if examples_dir.exists():
        for item in sorted(examples_dir.iterdir()):
            if item.is_dir():
                readme = item / "README.md"
                if readme.exists():
                    content = readme.read_text(encoding="utf-8", errors="ignore")
                    title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
                    title = title_match.group(1) if title_match else item.name
                    cookbooks.append({
                        "type": "cookbook",
                        "name": item.name,
                        "title": title,
                        "description": extract_first_section(content, 200),
                        "path": str(readme.relative_to(KB_DIR)),
                        "repo": "openai-cookbook",
                        "tags": _extract_tags(content, {}),
                    })

    # anthropic-cookbook patterns
    patterns_dir = SOURCES_DIR / "anthropic-cookbook"
    if patterns_dir.exists():
        for item in sorted(patterns_dir.iterdir()):
            if item.is_dir():
                readme = item / "README.md"
                if not readme.exists():
                    continue
                content = readme.read_text(encoding="utf-8", errors="ignore")
                title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
                title = title_match.group(1) if title_match else item.name
                cookbooks.append({
                    "type": "cookbook",
                    "name": item.name,
                    "title": title,
                    "description": extract_first_section(content, 200),
                    "path": str(readme.relative_to(KB_DIR)),
                    "repo": "anthropic-cookbook",
                    "tags": _extract_tags(content, {}),
                })

    # gemini-cookbook
    gemini_dir = SOURCES_DIR / "google-gemini-cookbook"
    if gemini_dir.exists():
        for item in sorted(gemini_dir.iterdir()):
            if item.is_dir() and not item.name.startswith('.'):
                readme = item / "README.md"
                if not readme.exists():
                    continue
                content = readme.read_text(encoding="utf-8", errors="ignore")
                title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
                title = title_match.group(1) if title_match else item.name
                cookbooks.append({
                    "type": "cookbook",
                    "name": item.name,
                    "title": title,
                    "description": extract_first_section(content, 200),
                    "path": str(readme.relative_to(KB_DIR)),
                    "repo": "google-gemini-cookbook",
                    "tags": _extract_tags(content, {}),
                })

    return cookbooks


def _extract_tags(content: str, meta: dict) -> list:
    """Extract searchable tags from content."""
    tags = set()
    content_lower = content.lower()

    # Technology tags
    tech_keywords = {
        "python": "python", "typescript": "typescript", "javascript": "javascript",
        "csharp": "csharp", "dotnet": "dotnet", "java": "java", "rust": "rust",
        "openpyxl": "excel", "xlsx": "excel", "spreadsheet": "excel",
        "docx": "word", "document": "word",
        "pdf": "pdf", "pptx": "powerpoint",
        "mcp": "mcp", "fastmcp": "mcp",
        "graph api": "graph-api", "sharepoint": "sharepoint",
        "azure": "azure", "aws": "aws", "gcp": "gcp",
        "openai": "openai", "gpt": "openai",
        "anthropic": "anthropic", "claude": "anthropic",
        "gemini": "gemini", "vertex": "gemini",
        "sql": "sql", "database": "database",
        "slack": "slack", "teams": "teams",
        "jira": "jira", "github": "github",
        "docker": "docker", "kubernetes": "kubernetes",
    }

    for keyword, tag in tech_keywords.items():
        if keyword in content_lower:
            tags.add(tag)

    # Domain tags
    domain_keywords = {
        "financial": "finance", "dcf": "finance", "valuation": "finance",
        "sales": "sales", "crm": "sales", "pipeline": "sales",
        "legal": "legal", "contract": "legal", "compliance": "legal",
        "marketing": "marketing", "seo": "marketing", "campaign": "marketing",
        "support": "support", "ticket": "support", "escalation": "support",
        "engineering": "engineering", "code review": "engineering",
        "design": "design", "ux": "design", "accessibility": "design",
        "hr": "hr", "recruiting": "hr", "onboarding": "hr",
        "operations": "operations", "runbook": "operations",
        "product": "product-management", "roadmap": "product-management",
        "data analysis": "data", "analytics": "data", "visualization": "data",
        "security": "security", "authentication": "security", "rbac": "security",
    }

    for keyword, tag in domain_keywords.items():
        if keyword in content_lower:
            tags.add(tag)

    return sorted(tags)


def _extract_tags_from_plugin(data: dict, skills: list, commands: list) -> list:
    """Extract tags from plugin metadata."""
    tags = set()
    desc = (data.get("description", "") + " ".join(skills) + " ".join(commands)).lower()

    for keyword, tag in {
        "financial": "finance", "sales": "sales", "legal": "legal",
        "marketing": "marketing", "support": "support", "engineering": "engineering",
        "design": "design", "hr": "hr", "operations": "operations",
        "product": "product-management", "data": "data", "search": "search",
        "azure": "azure", "excel": "excel", "document": "word",
    }.items():
        if keyword in desc:
            tags.add(tag)

    return sorted(tags)


def build_catalog() -> dict:
    """Build complete catalog."""
    skills = scan_skill_files()
    plugins = scan_plugins()
    cookbooks = scan_cookbooks()

    catalog = {
        "version": "1.0",
        "generated": __import__("datetime").datetime.now().isoformat(),
        "stats": {
            "skills": len(skills),
            "plugins": len(plugins),
            "cookbooks": len(cookbooks),
            "total": len(skills) + len(plugins) + len(cookbooks),
        },
        "entries": skills + plugins + cookbooks,
    }

    return catalog


def search_catalog(catalog: dict, query: str, top_k: int = 10) -> list:
    """Simple keyword search in catalog."""
    query_terms = set(query.lower().split())
    results = []

    for entry in catalog["entries"]:
        # Build searchable text
        searchable = " ".join([
            entry.get("name", ""),
            entry.get("description", ""),
            entry.get("title", ""),
            " ".join(entry.get("tags", [])),
            " ".join(entry.get("triggers", [])),
            " ".join(entry.get("skills", [])),
            " ".join(entry.get("commands", [])),
            entry.get("repo", ""),
        ]).lower()

        # Score: count matching terms
        score = sum(1 for t in query_terms if t in searchable)
        # Bonus for exact phrase match
        if query.lower() in searchable:
            score += 2

        if score > 0:
            results.append((entry, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]


def main():
    parser = argparse.ArgumentParser(description="Build Skills Catalog")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    parser.add_argument("--search", help="Search catalog")
    parser.add_argument("--top", type=int, default=10, help="Number of results")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    # Build or load catalog
    if args.search and CATALOG_PATH.exists():
        catalog = json.loads(CATALOG_PATH.read_text())
    else:
        print("Building catalog...", file=__import__("sys").stderr)
        catalog = build_catalog()
        CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
        print(f"Catalog saved to {CATALOG_PATH}", file=__import__("sys").stderr)

    if args.stats:
        stats = catalog["stats"]
        if args.json:
            print(json.dumps(stats, indent=2))
            return

        print(f"\n=== Skills Catalog ===\n")
        print(f"  Skills (SKILL.md):  {stats['skills']}")
        print(f"  Plugins:            {stats['plugins']}")
        print(f"  Cookbooks:          {stats['cookbooks']}")
        print(f"  Total entries:      {stats['total']}")

        # Tags distribution
        tag_counts = defaultdict(int)
        for entry in catalog["entries"]:
            for tag in entry.get("tags", []):
                tag_counts[tag] += 1

        print(f"\n  Top tags:")
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
            print(f"    {tag}: {count}")

        # By repo
        repo_counts = defaultdict(int)
        for entry in catalog["entries"]:
            repo_counts[entry.get("repo", "?")] += 1

        print(f"\n  By repository:")
        for repo, count in sorted(repo_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"    {repo}: {count}")
        return

    if args.search:
        results = search_catalog(catalog, args.search, args.top)

        if args.json:
            print(json.dumps([{"entry": e, "score": s} for e, s in results],
                             ensure_ascii=False, indent=2))
            return

        print(f"\n=== Catalog Search: '{args.search}' ({len(results)} results) ===\n")
        for i, (entry, score) in enumerate(results, 1):
            etype = entry["type"]
            name = entry.get("title", entry["name"])
            desc = entry.get("description", "")[:100]
            tags = ", ".join(entry.get("tags", [])[:5])
            path = entry.get("path", "")

            print(f"  {i}. [{etype}] {name}")
            print(f"     {desc}")
            print(f"     Path: {path}")
            if tags:
                print(f"     Tags: {tags}")
            if entry.get("triggers"):
                print(f"     Triggers: {', '.join(entry['triggers'][:3])}")
            if entry.get("skills"):
                print(f"     Skills: {', '.join(entry['skills'][:5])}")
            print()
        return

    # Default: just build and show stats
    stats = catalog["stats"]
    print(f"\nCatalog built: {stats['total']} entries ({stats['skills']} skills, {stats['plugins']} plugins, {stats['cookbooks']} cookbooks)")


if __name__ == "__main__":
    main()
