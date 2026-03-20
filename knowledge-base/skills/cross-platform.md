# Cross-Platform Skills & Patterns

## Skills definice podle platformy

### Jak platformy definují "skills"

| Platforma | Formát | Umístění | Discovery |
|-----------|--------|----------|-----------|
| Claude Code | SKILL.md (markdown) | .claude/skills/ | Automaticky při spuštění |
| GitHub Copilot | .md + agents.md | .github/copilot/ | VS Code settings `chat.agent.skills` |
| Cursor | .cursorrules + .cursor/rules/ | Root projektu | Automaticky |
| Copilot Studio | Topics + Actions (GUI) | Power Platform | Přes Studio UI |
| Semantic Kernel | @kernel_function (Python/C#) | Plugin třídy | Registrace v kernelu |
| OpenAI | JSON Schema (function calling) | API request | Přes tools parameter |
| MCP | Tools + Resources + Prompts | MCP server | Protocol discovery |

### Společná anatomie skill

Každá platforma má svůj formát, ale sdílejí společné elementy:

```
SKILL = {
  name: string           # Identifikátor
  description: string    # Co skill dělá (pro LLM)
  inputs: Schema         # Parametry (JSON Schema / Zod / annotations)
  instructions: string   # Jak skill použít (prompt / kód)
  tools: string[]        # Jaké nástroje skill potřebuje
}
```

## Pattern: Progressive Disclosure (Microsoft Agent Skills)

Microsoft zavádí 3-úrovňový loading pro efektivní skills:

1. **Discovery** - Krátký popis (pár řádků), stačí k rozhodnutí zda skill použít
2. **Instructions** - Detailní instrukce jak skill provést
3. **Resources** - Plné reference, API docs, příklady

Tento pattern šetří tokeny a kontext window.

## Instalace skills podle platformy

### Claude Code
```bash
# Skills se dávají do .claude/skills/
mkdir -p .claude/skills/azure-devops/
cat > .claude/skills/azure-devops/SKILL.md << 'EOF'
---
name: azure-devops
description: Manage Azure DevOps work items, repos, and pipelines
tools: Bash
---
# Azure DevOps Skill
Use `az devops` CLI commands to interact with Azure DevOps.
## Work Items
- `az boards work-item create --type "Task" --title "..."`
- `az boards work-item show --id N`
## Repos
- `az repos list`
- `az repos pr create --title "..." --source-branch "..."`
EOF
```

### GitHub Copilot (VS Code)
```bash
# Skills from MicrosoftDocs/Agent-Skills
mkdir -p .github/skills/
# Zkopírovat skills z https://github.com/MicrosoftDocs/Agent-Skills
# Aktivovat v VS Code: Settings → chat.agent.skills → Enable
```

### Cursor
```bash
# Rules/skills přes .cursor/rules/
mkdir -p .cursor/rules/
cat > .cursor/rules/azure.mdc << 'EOF'
---
description: Azure development patterns
globs: ["**/azure/**", "**/infra/**"]
---
# Azure Rules
- Use Azure CLI (`az`) for resource management
- Follow Azure naming conventions: {resource}-{env}-{region}-{instance}
- Always use managed identity over connection strings
EOF
```

### Copilot Studio
```
# V Copilot Studio UI:
1. Topics → New Topic → popis scenáře
2. Actions → Add connector action → vybrat Power Platform connector
3. Generative AI → Enable orchestration
```

## Cross-Platform Skills Matrix pro M365/Azure

| Operace | Claude Code | Copilot | Cursor | Copilot Studio |
|---------|-------------|---------|--------|----------------|
| Azure resources | az CLI skill | @azure agent | MCP/rules | Power Platform |
| SharePoint files | MCP server | Graph API skill | MCP server | SP connector |
| Outlook email | MCP M365 tools | Copilot agent | MCP server | Outlook connector |
| Azure DevOps | az devops CLI / MCP | @azure-devops | MCP server | ADO connector |
| Teams messages | Graph API | Built-in | MCP server | Teams connector |
| SQL queries | Bash + sqlcmd | DB extensions | MCP server | SQL connector |

## Best Practices napříč platformami

### 1. Popisujte CO, ne JAK
```
# Dobře:
description: "Find and summarize recent emails about project X"

# Špatně:
description: "Call Graph API endpoint /me/messages with filter..."
```

### 2. Minimalizujte tools
Dávejte skills jen nástroje, které opravdu potřebují.

### 3. Vždy testujte s reálným LLM
Skills jsou interpretované modelem - mohou se chovat jinak než čekáte.

### 4. Security first
- Nikdy nehardcodujte credentials
- Používejte managed identity kde to jde
- Validujte vstupy na hranici systému

### 5. Kompozice > monolity
Malé, fokusované skills které lze skládat jsou lepší než velké all-in-one.
