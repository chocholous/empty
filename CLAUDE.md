# AI Tools Knowledge Base — Discovery-First Agent

Knowledge base s 668 skills, pluginy a cookbooks z 15 repozitářů.
Agent **nemusí znát všechny use cases předem** — najde relevantní skill a naučí se ho použít.

## Hlavní princip: Discovery → Read → Execute

Když uživatel popíše problém:

1. **Hledej v katalogu** (668 skills, pluginů a cookbooks):
   ```bash
   python3 knowledge-base/tools/build-catalog.py --search "popis problému" --top 5
   ```

2. **Přečti nalezený SKILL.md** — obsahuje přesné instrukce, triggers, workflow, gotchas:
   ```bash
   # Katalog vrátí cestu, např: sources/anthropic-skills/skills/xlsx/SKILL.md
   # Přečti celý soubor a řiď se jeho instrukcemi
   ```

3. **Doplň z guides/skills** pokud potřebuješ kontext platformy nebo technologie (viz tabulky níže)

4. **Pokud katalog nic nevrátí**, použij semantic search přes celou KB:
   ```bash
   python3 knowledge-base/tools/semantic-search.py "popis problému" --top 10
   ```

## Katalog: 668 indexovaných zdrojů

```bash
# Hledat skill/plugin/cookbook pro konkrétní úkol
python3 knowledge-base/tools/build-catalog.py --search "excel porovnání" --top 5
python3 knowledge-base/tools/build-catalog.py --search "contract review" --top 5
python3 knowledge-base/tools/build-catalog.py --search "dcf valuation" --top 5
python3 knowledge-base/tools/build-catalog.py --search "azure deploy" --top 5

# Přehled katalogu
python3 knowledge-base/tools/build-catalog.py --stats

# Rebuild katalogu (po update sources)
python3 knowledge-base/tools/build-catalog.py
```

**Co je v katalogu:**
- 624 SKILL.md souborů (Anthropic, Microsoft, Google, OpenAI, community)
- 37 Claude pluginů (sales, legal, finance, PM, data, support, engineering, design, marketing, HR, operations)
- 7 cookbook tutoriálů

## Kdy použít který nástroj

| Situace | Nástroj |
|---------|---------|
| Uživatel chce splnit úkol (porovnat XLS, napsat smlouvu, DCF model) | `build-catalog.py --search` → přečíst SKILL.md |
| Potřebuju porozumět platformě (Claude Code, Copilot, Cursor) | Přečíst příslušný guide (viz tabulka) |
| Potřebuju porozumět technologii (MCP, Semantic Kernel, function calling) | Přečíst příslušný skill doc (viz tabulka) |
| Hledám napříč celou KB (přirozený jazyk) | `semantic-search.py "dotaz"` |
| Chci vědět co KB pokrývá | `discover.py coverage` nebo `build-catalog.py --stats` |
| Hledám vztahy mezi koncepty | `discover.py graph "node"` nebo `discover.py related "téma"` |

## Referenční tabulky (pokud katalog nestačí)

### Platformy → Guides

| Klíčová slova | Soubor |
|---------------|--------|
| Claude Code, `.claude/`, SKILL.md tvorba, hooks, agent SDK | [guides/claude-code.md](knowledge-base/guides/claude-code.md) |
| Claude Desktop, `claude_desktop_config.json` | [guides/claude-desktop.md](knowledge-base/guides/claude-desktop.md) |
| GitHub Copilot, `@workspace`, Copilot Extensions | [guides/github-copilot.md](knowledge-base/guides/github-copilot.md) |
| Copilot Studio, Topics, Actions, Power Platform | [guides/copilot-studio.md](knowledge-base/guides/copilot-studio.md) |
| Cursor, `.cursor/rules/`, `.mdc` soubory | [guides/cursor.md](knowledge-base/guides/cursor.md) |
| Terminal workflows, CLI, CI/CD | [guides/terminal.md](knowledge-base/guides/terminal.md) |

### Technologie → Skills

| Klíčová slova | Soubor |
|---------------|--------|
| MCP, FastMCP, Model Context Protocol | [skills/mcp-servers.md](knowledge-base/skills/mcp-servers.md) |
| Semantic Kernel, `@kernel_function`, Process Framework | [skills/semantic-kernel.md](knowledge-base/skills/semantic-kernel.md) |
| OpenAI, function calling, Agents SDK, Responses API | [skills/openai-tools.md](knowledge-base/skills/openai-tools.md) |
| M365, Graph API, SharePoint, Teams, Azure | [skills/m365-connectors.md](knowledge-base/skills/m365-connectors.md) |
| SKILL.md standard, cross-platform srovnání | [skills/cross-platform.md](knowledge-base/skills/cross-platform.md) |

### Sumarizované workflows (pro rychlý kontext)

| Téma | Soubor |
|------|--------|
| Excel, DOCX, PDF, PPTX — vzory a gotchas | [skills/document-skills.md](knowledge-base/skills/document-skills.md) |
| DCF, comps, LBO, merger, audit XLS, IB/ER/PE/WM | [skills/financial-workflows.md](knowledge-base/skills/financial-workflows.md) |
| Sales, legal, PM, data, support, enterprise search | [skills/office-workflows.md](knowledge-base/skills/office-workflows.md) |

## Nástroje

```bash
# Skills catalog (hlavní discovery nástroj)
python3 knowledge-base/tools/build-catalog.py --search "query"
python3 knowledge-base/tools/build-catalog.py --stats
python3 knowledge-base/tools/build-catalog.py --search "query" --json

# Semantic search (TF-IDF, přirozený jazyk)
python3 knowledge-base/tools/semantic-search.py "dotaz"
python3 knowledge-base/tools/semantic-search.py "dotaz" --top 10 --section skills

# Discovery (témata, vztahy, mezery)
python3 knowledge-base/tools/discover.py coverage
python3 knowledge-base/tools/discover.py topics --min-docs 2
python3 knowledge-base/tools/discover.py related "MCP"
python3 knowledge-base/tools/discover.py graph "copilot-studio"
python3 knowledge-base/tools/discover.py gaps

# Fulltext grep
./knowledge-base/tools/search.sh "azure devops"
```

## Struktura

```
knowledge-base/
├── catalog.json          # Auto-generated index (668 entries)
├── guides/               # 6 platform guides
├── skills/               # 8 technology + workflow guides
├── graph/                # Knowledge graph (30+ nodes, 40+ edges)
├── tools/                # Search, discovery, catalog builder
│   ├── build-catalog.py  # Skills catalog generator + search
│   ├── semantic-search.py
│   ├── discover.py
│   └── search.sh
└── sources/              # 15 source repos (6,200+ docs, raw SKILL.md files)
    ├── anthropic-skills/                  # 18 reference skills
    ├── anthropic-knowledge-work-plugins/  # 11 domain plugins (142 skills)
    ├── anthropic-financial-services-plugins/  # 6 finance plugins (63 skills)
    ├── anthropic-cookbook/                 # Tutorials, examples
    ├── microsoft-agent-skills/            # 181 agent skills
    ├── microsoftdocs-agent-skills/        # 192 Azure skills
    ├── microsoft-azure-skills/            # 55 Azure deployment skills
    ├── openai-cookbook/                    # Function calling, Agents SDK
    ├── google-gemini-cookbook/             # Multimodal, Live API
    └── ...                                # + 6 dalších repozitářů
```

## Zdroje dat (15 repozitářů)

### Anthropic
- [anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook) — Tool use, MCP, Agent SDK, RAG
- [anthropics/skills](https://github.com/anthropics/skills) — SKILL.md open standard (18 reference skills)
- [anthropics/anthropic-claude-quickstarts](https://github.com/anthropics/anthropic-claude-quickstarts) — Agent framework, MCP integration
- [anthropics/anthropic-financial-services-plugins](https://github.com/anthropics/anthropic-financial-services-plugins) — 6 finance plugins (63 skills)
- [anthropics/anthropic-knowledge-work-plugins](https://github.com/anthropics/anthropic-knowledge-work-plugins) — 11 domain plugins (142 skills)

### Microsoft
- [microsoft/skills](https://github.com/microsoft/skills) — 181 agent skills, 4 jazyky
- [microsoft/azure-skills](https://github.com/microsoft/azure-skills) — 55 Azure skills
- [microsoft/copilot-studio-samples](https://github.com/microsoft/copilot-studio-samples) — MCP, A2A, M365 Agents SDK
- [microsoft/PowerPlatformConnectors](https://github.com/microsoft/PowerPlatformConnectors) — 1,400+ connectors
- [MicrosoftDocs/Agent-Skills](https://github.com/MicrosoftDocs/Agent-Skills) — 192 Azure skills

### OpenAI / Azure
- [openai/openai-cookbook](https://github.com/openai/openai-cookbook) — Function calling, Agents SDK, Swarm
- [azure-samples/openai](https://github.com/Azure-Samples/openai) — Customer assist, Semantic Kernel Process

### Google
- [google/gemini-cookbook](https://github.com/google/gemini-cookbook) — Multimodal, function calling, Live API
- [google/gemini-skills](https://github.com/google/gemini-skills) — Gemini API, Interactions API, Vertex AI

### Community
- [pnp/copilot-pro-dev-samples](https://github.com/pnp/copilot-pro-dev-samples) — 70+ M365 Copilot declarative agents
