# AI Tools Knowledge Base

Toto je knowledge base pro práci s AI nástroji napříč platformami.
Obsahuje skills, commands, best practices, MCP tools a connectors pro M365/Azure.

## Struktura

```
knowledge-base/
├── guides/              # Per-stack návody
│   ├── claude-code.md        # Claude Code (terminal + VSCode)
│   ├── claude-desktop.md     # Claude Desktop app
│   ├── github-copilot.md     # GitHub Copilot (VSCode + CLI)
│   ├── copilot-studio.md     # Microsoft Copilot Studio
│   ├── cursor.md             # Cursor IDE
│   └── terminal.md           # Terminal-only workflows
├── skills/              # Skills definice a katalogy
│   ├── mcp-servers.md        # MCP servery - oficiální + community
│   ├── semantic-kernel.md    # Semantic Kernel plugins/skills
│   ├── openai-tools.md       # OpenAI function calling & GPT Actions
│   ├── m365-connectors.md    # M365/Azure skills a connectors
│   └── cross-platform.md     # Společné patterny napříč platformami
├── graph/               # Knowledge graph
│   └── knowledge-graph.json  # Vztahy mezi koncepty
├── tools/               # Nástroje pro vyhledávání
│   ├── search.sh             # Fulltext search v KB
│   └── update-sources.sh     # Aktualizace ze zdrojových repozitářů
└── sources/             # Reference na zdrojové repozitáře
    ├── repos.json            # Seznam zdrojových repozitářů s metadaty
    ├── mcp/                  # MCP-related extracts
    ├── openai/               # OpenAI cookbook extracts
    ├── anthropic/            # Anthropic cookbook extracts
    └── microsoft/            # Microsoft SK/Copilot extracts
```

## Rychlé vyhledávání

```bash
# Hledat napříč celou KB
./knowledge-base/tools/search.sh "azure devops"

# Hledat jen v guides
grep -r "azure" knowledge-base/guides/

# Otevřít knowledge graph
cat knowledge-base/graph/knowledge-graph.json | jq '.nodes[] | select(.tags | contains(["m365"]))'
```

## Tech stack návody

| Stack | Soubor | Popis |
|-------|--------|-------|
| Claude Code | [guides/claude-code.md](knowledge-base/guides/claude-code.md) | Terminal + VSCode extension, MCP, skills, CLAUDE.md |
| Claude Desktop | [guides/claude-desktop.md](knowledge-base/guides/claude-desktop.md) | Desktop app, MCP konfigurace, projekty |
| GitHub Copilot | [guides/github-copilot.md](knowledge-base/guides/github-copilot.md) | Chat, extensions, skills, @agents |
| Copilot Studio | [guides/copilot-studio.md](knowledge-base/guides/copilot-studio.md) | Topics, actions, Power Platform connectors |
| Cursor | [guides/cursor.md](knowledge-base/guides/cursor.md) | Rules, MCP, AI composer, chat |
| Terminal | [guides/terminal.md](knowledge-base/guides/terminal.md) | CLI-only workflows, Claude Code, Codex |

## Zdroje dat (jen HIGH kvalita)

### Microsoft (oficiální)
- [microsoft/mcp](https://github.com/microsoft/mcp) - MCP katalog: Azure 40+ services, M365, AKS, Foundry (2.8k stars)
- [microsoft/skills](https://github.com/microsoft/skills) - Oficiální skills, MCP servery, Agents.md pro coding agents
- [MicrosoftDocs/Agent-Skills](https://github.com/MicrosoftDocs/Agent-Skills) - Kurátované agent skills pro VS Code
- [MicrosoftDocs/mcp](https://github.com/MicrosoftDocs/mcp) - MS Learn MCP Server (docs pro LLMs)
- [microsoft/azure-devops-mcp](https://github.com/microsoft/azure-devops-mcp) - Azure DevOps MCP (1.4k stars)
- [microsoft/semantic-kernel](https://github.com/microsoft/semantic-kernel) - AI orchestration s M365 plugins (22k stars)
- [microsoft/GitHub-Copilot-for-Azure](https://github.com/microsoft/GitHub-Copilot-for-Azure) - Copilot for Azure extension
- [dotnet/skills](https://github.com/dotnet/skills) - .NET agent skills

### GitHub / Copilot
- [github/awesome-copilot](https://github.com/github/awesome-copilot) - 175+ agents, 208+ skills, 48+ plugins
- [copilot-extensions](https://github.com/copilot-extensions) - Copilot Extensions SDK + samples

### Anthropic / MCP
- [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) - Oficiální MCP servery (10k+ stars)
- [modelcontextprotocol/typescript-sdk](https://github.com/modelcontextprotocol/typescript-sdk) - MCP TypeScript SDK
- [anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook) - Tool use, MCP, agent SDK

### OpenAI
- [openai/openai-cookbook](https://github.com/openai/openai-cookbook) - Function calling, GPT Actions, Agents SDK (60k stars)

### Community
- [sickn33/antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills) - 1273+ skills, multi-platform (25k stars)

Aktualizace: `./knowledge-base/tools/update-sources.sh`
