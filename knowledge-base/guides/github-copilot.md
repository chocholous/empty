# GitHub Copilot - Kompletní průvodce

## Přehled

GitHub Copilot je AI pair programmer integrovaný do VS Code, Visual Studio, JetBrains a CLI.

## Skills & Agents v Copilot

### Built-in agents (@ mentions)
| Agent | Popis |
|-------|-------|
| @workspace | Kontext celého projektu, hledá v souborech |
| @terminal | Terminálové příkazy a output |
| @vscode | VS Code nastavení a extensions |
| @azure | Azure operace (s Copilot for Azure extension) |

### Slash commands
| Command | Popis |
|---------|-------|
| /explain | Vysvětli vybraný kód |
| /fix | Oprav chybu v kódu |
| /tests | Generuj testy |
| /doc | Generuj dokumentaci |
| /new | Nový projekt scaffold |
| /newNotebook | Nový Jupyter notebook |

### Custom skills (VS Code)

#### Instalace Microsoft Agent Skills
```bash
# 1. Klonovat MicrosoftDocs/Agent-Skills
git clone https://github.com/MicrosoftDocs/Agent-Skills.git

# 2. Zkopírovat skills do projektu
cp -r Agent-Skills/skills/ .github/skills/

# 3. Aktivovat v VS Code
# Settings → chat.agent.skills → Enable
```

#### Vlastní instructions
```markdown
<!-- .github/copilot-instructions.md -->
# Project Instructions for Copilot

## Coding Standards
- Use TypeScript strict mode
- Follow Azure naming conventions
- All Azure resources must use managed identity

## Architecture
- Microservices on Azure Container Apps
- Event-driven with Azure Service Bus
- Data in Azure Cosmos DB
```

### GitHub Copilot Extensions (DEPRECATED → MCP)

> **Pozor:** Copilot Extensions (GitHub App-based) byly **deprecated v listopadu 2025** a nahrazeny MCP.
> Nové integrace stavějte jako MCP servery - fungují v Copilot, Claude Code i Cursor.

#### Co je nahradilo
- **MCP servery** - build once, use everywhere
- **GitHub MCP Registry** - kurátovaný adresář MCP serverů
- **Awesome Copilot plugins** - community ekosystém

#### Oficiální Azure Extensions (stále funkční)
- **GitHub Copilot for Azure** - Přímá integrace Azure služeb
  - Resource management, deployment, monitoring
  - [microsoft/GitHub-Copilot-for-Azure](https://github.com/microsoft/GitHub-Copilot-for-Azure)

### Multi-Agent v VS Code (od v1.109, Jan 2026)

Claude, Codex a Copilot fungují společně ve VS Code:

#### Third-party agents
- Claude běží jako agent přímo v Copilot Chat
- Aktivace: `github.copilot.chat.claudeAgent.enabled`
- Vyžaduje Copilot Pro+ nebo Enterprise
- Billing přes GitHub (žádný separátní Anthropic subscription)
- Unified **Agent Sessions** view

#### Agent HQ (GitHub Issues)
- Přiřaďte issue @Copilot, @Claude, nebo @Codex
- Agenti submitují draft PRs k review
- Mention agenty v PR komentářích pro follow-up
- Porovnávejte výstupy více agentů na stejném issue

#### Doporučení pro kombinaci
```
Copilot → inline completions, quick chat, @workspace
Claude  → complex reasoning, multi-file refactors, architecture
Codex   → autonomous coding tasks, background PR generation
```

### Agents.md (z microsoft/skills)

```markdown
<!-- agents.md v root projektu -->
# Agent Configuration

## Skills
- azure-devops: Manage work items and pipelines
- azure-resources: Deploy and manage Azure resources

## Tools
- az CLI for Azure operations
- gh CLI for GitHub operations
```

## Awesome Copilot ekosystém

[github/awesome-copilot](https://github.com/github/awesome-copilot):
- **175+ agents** - Domain-specific AI agents
- **208+ skills** - Reusable skill definitions
- **176+ instructions** - Custom instruction sets
- **48+ plugins** - Bundled agent+skill packages
- **7 agentic workflows** - Complete workflow definitions

### Plugin bundles dostupné pro:
- Azure Cloud development
- Frontend development
- Python/Django/FastAPI
- .NET development
- DevOps/Infrastructure
- Security auditing

## MCP v Copilot

VS Code Copilot Chat podporuje MCP servery:
1. Settings → MCP → Add Server
2. Konfigurovat command + args
3. MCP tools jsou dostupné v Copilot Chat

## M365/Azure workflow s Copilot

```
1. Nainstalovat GitHub Copilot for Azure extension
2. Přidat Microsoft Agent Skills (.github/skills/)
3. Nastavit copilot-instructions.md s Azure konvencemi
4. Použít @azure agent pro Azure operace
5. MCP servery pro rozšířený přístup k Azure/M365
```

## Best Practices

1. **copilot-instructions.md** - Projekt-specifické instrukce
2. **Agent Skills** - Instalovat relevantní skills z MicrosoftDocs/Agent-Skills
3. **@workspace** - Pro codebase-wide otázky
4. **Extensions** - Pro integraci s firemními nástroji
5. **MCP** - Pro přístup k datovým zdrojům

## Zdroje

- [github/awesome-copilot](https://github.com/github/awesome-copilot)
- [MicrosoftDocs/Agent-Skills](https://github.com/MicrosoftDocs/Agent-Skills)
- [copilot-extensions](https://github.com/copilot-extensions)
- [microsoft/GitHub-Copilot-for-Azure](https://github.com/microsoft/GitHub-Copilot-for-Azure)
- [microsoft/skills](https://github.com/microsoft/skills)
