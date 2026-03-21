# AI Tools Knowledge Base — Agent Router

Toto je knowledge base pro práci s AI nástroji napříč platformami (15 repozitářů, 6,200+ zdrojových dokumentů).
Obsahuje skills, commands, best practices, MCP tools a connectors pro M365/Azure/Google/OpenAI.

## Routing pravidla

Při dotazu na konkrétní téma, **VŽDY načti příslušný soubor** z knowledge-base/ a odpovídej na základě jeho obsahu.

### Dotaz na platformu → Guides

| Klíčová slova | Soubor |
|---------------|--------|
| Claude Code, `.claude/`, SKILL.md tvorba, terminal AI, hooks, agent SDK | [guides/claude-code.md](knowledge-base/guides/claude-code.md) |
| Claude Desktop, desktop app, `claude_desktop_config.json` | [guides/claude-desktop.md](knowledge-base/guides/claude-desktop.md) |
| GitHub Copilot, `@workspace`, `@azure`, Copilot Extensions, `.github/skills/` | [guides/github-copilot.md](knowledge-base/guides/github-copilot.md) |
| Copilot Studio, Topics, Actions, Power Platform, declarative agents | [guides/copilot-studio.md](knowledge-base/guides/copilot-studio.md) |
| Cursor, `.cursor/rules/`, `.mdc` soubory, Cursor AI | [guides/cursor.md](knowledge-base/guides/cursor.md) |
| Terminal workflows, CLI, CI/CD, scripting, pipe, batch AI | [guides/terminal.md](knowledge-base/guides/terminal.md) |

### Dotaz na technologii → Skills

| Klíčová slova | Soubor |
|---------------|--------|
| MCP, Model Context Protocol, MCP server, FastMCP, tools/resources/prompts | [skills/mcp-servers.md](knowledge-base/skills/mcp-servers.md) |
| Semantic Kernel, SK, `@kernel_function`, Process Framework, SK agents | [skills/semantic-kernel.md](knowledge-base/skills/semantic-kernel.md) |
| OpenAI, function calling, GPT Actions, Agents SDK, Responses API, Swarm | [skills/openai-tools.md](knowledge-base/skills/openai-tools.md) |
| M365, Graph API, connectors, SharePoint, Outlook, Teams, Azure services | [skills/m365-connectors.md](knowledge-base/skills/m365-connectors.md) |
| Cross-platform, SKILL.md standard, skills srovnání, progressive disclosure | [skills/cross-platform.md](knowledge-base/skills/cross-platform.md) |

### Dotaz na vztahy/přehled → Knowledge Graph

| Typ dotazu | Příkaz |
|-----------|--------|
| Které platformy podporují MCP? | Načti `graph/knowledge-graph.json`, filtruj `nodes[tags contains 'mcp']` |
| Jaké skills existují pro Azure? | Filtruj `nodes[tags contains 'azure']` + `edges[relation=provides_skills_for]` |
| Jak spolu souvisí X a Y? | Hledej v `edges` propojení mezi node ID |

### Fulltext hledání

```bash
./knowledge-base/tools/search.sh "azure devops"
./knowledge-base/tools/search.sh "MCP" --section guides
./knowledge-base/tools/search.sh "SharePoint" --section skills
```

## Struktura knowledge base

```
knowledge-base/
├── guides/              # Per-stack návody (6 platforem)
│   ├── claude-code.md        # Claude Code + Agent SDK + plugins
│   ├── claude-desktop.md     # Desktop app + MCP + M365 connector
│   ├── github-copilot.md     # Copilot + Agent Skills + declarative agents
│   ├── copilot-studio.md     # Topics, actions, MCP, A2A, TypeSpec
│   ├── cursor.md             # Rules (.mdc), MCP, AI composer
│   └── terminal.md           # CLI workflows, Claude Code, Codex
├── skills/              # Technologie a patterny
│   ├── mcp-servers.md        # MCP servery + FastMCP + Azure MCP + Gemini
│   ├── semantic-kernel.md    # SK plugins, agents, Process Framework, memory
│   ├── openai-tools.md       # Function calling, Agents SDK, Structured Outputs
│   ├── m365-connectors.md    # Graph API, Power Platform, Azure AI Search
│   └── cross-platform.md     # SKILL.md standard, srovnání platforem
├── graph/               # Knowledge graph
│   └── knowledge-graph.json  # 30+ nodes, 40+ edges, vztahy mezi koncepty
├── tools/               # Nástroje
│   ├── search.sh             # Fulltext search v KB
│   └── update-sources.sh     # Aktualizace ze zdrojových repozitářů
└── sources/             # 15 zdrojových repozitářů (extrahovaný obsah)
    ├── repos.json
    ├── anthropic-cookbook/    anthropic-skills/    anthropic-financial-services-plugins/
    ├── anthropic-knowledge-work-plugins/    anthropic-claude-quickstarts/
    ├── microsoft-agent-skills/    microsoft-azure-skills/    microsoft-copilot-studio-samples/
    ├── microsoft-power-platform-connectors/    microsoftdocs-agent-skills/
    ├── openai-cookbook/    azure-samples-openai/
    ├── google-gemini-cookbook/    google-gemini-skills/
    └── pnp-copilot-pro-dev-samples/
```

## Quick Reference — nejčastější úkoly

### Vytvořit SKILL.md
→ Načti [skills/cross-platform.md](knowledge-base/skills/cross-platform.md) (formát, best practices, příklady)

### Postavit MCP server
→ Načti [skills/mcp-servers.md](knowledge-base/skills/mcp-servers.md) (FastMCP pattern, TypeScript/Python, annotations)

### Nastavit MCP pro Claude/Cursor/Copilot
→ Načti příslušný guide + [skills/mcp-servers.md](knowledge-base/skills/mcp-servers.md) (konfigurace podle platformy)

### Integrace s M365 (Graph API, SharePoint, Teams)
→ Načti [skills/m365-connectors.md](knowledge-base/skills/m365-connectors.md) + [guides/copilot-studio.md](knowledge-base/guides/copilot-studio.md)

### Multi-agent orchestrace
→ Načti [skills/semantic-kernel.md](knowledge-base/skills/semantic-kernel.md) (Process Framework) + [skills/openai-tools.md](knowledge-base/skills/openai-tools.md) (Swarm pattern) + [guides/claude-code.md](knowledge-base/guides/claude-code.md) (Agent SDK)

### Azure deployment/diagnostics
→ Načti [skills/m365-connectors.md](knowledge-base/skills/m365-connectors.md) (Azure AI Skills) + `graph/knowledge-graph.json` → `microsoft-azure-skills` node

### Copilot Studio agent s MCP
→ Načti [guides/copilot-studio.md](knowledge-base/guides/copilot-studio.md) (MCP integration, A2A, declarative agents, TypeSpec)

### Srovnání platforem
→ Načti [skills/cross-platform.md](knowledge-base/skills/cross-platform.md) (srovnávací matice, skills formáty)

## Zdroje dat (15 repozitářů)

### Anthropic
- [anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook) — Tool use, MCP, Agent SDK, RAG
- [anthropics/skills](https://github.com/anthropics/skills) — SKILL.md open standard (17 reference skills)
- [anthropics/anthropic-claude-quickstarts](https://github.com/anthropics/anthropic-claude-quickstarts) — Agent framework, MCP integration
- [anthropics/anthropic-financial-services-plugins](https://github.com/anthropics/anthropic-financial-services-plugins) — Finance plugins (DCF, comps, LBO)
- [anthropics/anthropic-knowledge-work-plugins](https://github.com/anthropics/anthropic-knowledge-work-plugins) — Enterprise plugins (sales, legal, bio-research)

### Microsoft
- [microsoft/skills](https://github.com/microsoft/skills) — 133 agent skills, 4 jazyky, Agents.md
- [microsoft/azure-skills](https://github.com/microsoft/azure-skills) — 22 Azure skills, deployment chain
- [microsoft/copilot-studio-samples](https://github.com/microsoft/copilot-studio-samples) — MCP, A2A, M365 Agents SDK
- [microsoft/PowerPlatformConnectors](https://github.com/microsoft/PowerPlatformConnectors) — 1,400+ connectors
- [MicrosoftDocs/Agent-Skills](https://github.com/MicrosoftDocs/Agent-Skills) — 193 Azure skills

### OpenAI / Azure
- [openai/openai-cookbook](https://github.com/openai/openai-cookbook) — Function calling, Agents SDK, Swarm
- [azure-samples/openai](https://github.com/Azure-Samples/openai) — Customer assist, Semantic Kernel Process

### Google
- [google/gemini-cookbook](https://github.com/google/gemini-cookbook) — Multimodal, function calling, Live API
- [google/gemini-skills](https://github.com/google/gemini-skills) — Gemini API, Interactions API, Vertex AI

### Community
- [pnp/copilot-pro-dev-samples](https://github.com/pnp/copilot-pro-dev-samples) — 70+ M365 Copilot declarative agents
