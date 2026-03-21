# Claude Code - Kompletní průvodce

## Co je Claude Code

CLI nástroj od Anthropic pro AI-assisted coding. Funguje v terminálu i jako VS Code extension.

## Instalace

```bash
# Terminal
npm install -g @anthropic-ai/claude-code
# Nebo přes npx
npx @anthropic-ai/claude-code

# VS Code
# Marketplace → "Claude Code" → Install
```

## Skills systém

### Struktura .claude adresáře
```
.claude/
├── CLAUDE.md              # Hlavní instrukce pro projekt
├── settings.json          # Konfigurace (permissions, hooks, MCP)
├── settings.local.json    # Lokální overrides (gitignored)
├── agents/                # Custom agenti
│   └── reviewer.md
├── commands/              # Slash commands
│   └── deploy.md
├── skills/                # Skills
│   └── azure-ops/
│       ├── SKILL.md       # Skill definice
│       └── runbook.md     # Podpůrné soubory
└── hooks/                 # Post-tool hooks
    └── logger.py
```

### SKILL.md formát
```yaml
---
name: azure-devops-manager
description: Manage Azure DevOps work items, repos, and pipelines
tools: Bash, Read, Grep, Glob
---
# Azure DevOps Management

## Práce s work items
- List: `az boards work-item list --project "MyProject"`
- Create: `az boards work-item create --type "Task" --title "..." --project "MyProject"`
- Update: `az boards work-item update --id N --state "Active"`

## Pull requests
- Create: `az repos pr create --title "..." --source-branch "feature/x" --target-branch "main"`
- List: `az repos pr list --status active`

## Pipelines
- Run: `az pipelines run --name "CI" --branch "main"`
- List: `az pipelines list`
```

### Custom commands (slash commands)
```yaml
# .claude/commands/deploy.md
---
name: deploy
description: Deploy to Azure environment
allowed-tools: Bash, Read
---
Deploy the current branch to the specified Azure environment.
1. Run tests first
2. Build the project
3. Deploy using `az webapp deploy`
```

Použití: `/deploy staging`

### Custom agents
```yaml
# .claude/agents/code-reviewer.md
---
name: code-reviewer
description: Performs thorough code reviews
tools: Read, Grep, Glob, Bash
---
Review the code changes focusing on:
- Security vulnerabilities
- Performance issues
- Code style consistency
- Test coverage
```

## MCP konfigurace

### Přidání MCP serverů
```bash
# CLI přidání
claude mcp add memory -- npx -y @modelcontextprotocol/server-memory
claude mcp add azure-devops -- npx -y @azure-devops/mcp YourOrgName
claude mcp add ms-docs -- npx -y @microsoftdocs/mcp

# Import z Claude Desktop
claude mcp add-from-claude-desktop

# JSON import
claude mcp add-json azure '{"command":"npx","args":["-y","@azure/mcp@latest","server","start"]}'
```

### Scopes
- **User:** `~/.claude.json` - globální
- **Project:** `.mcp.json` - pro projekt (commitovat do repo)
- **Local:** `.claude/settings.local.json` - lokální (gitignored)

Secrets v `.mcp.json`: použijte `${VAR}` syntax → načte z env.

### V settings.json (manuálně)
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": { "MEMORY_FILE_PATH": ".claude/memory.jsonl" }
    },
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start"]
    },
    "azure-devops": {
      "command": "npx",
      "args": ["-y", "@azure-devops/mcp", "YourOrgName"]
    },
    "ms-docs": {
      "command": "npx",
      "args": ["-y", "@microsoftdocs/mcp"]
    }
  }
}
```

### Claude Code jako MCP Server
Claude Code může sám fungovat jako MCP server:
```bash
claude mcp serve
```
Jiní klienti (Claude Desktop, Cursor) pak mohou volat Claude Code remotely.

## Hooks

```json
// settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "echo 'Tool used: $TOOL_NAME' >> .claude/audit.log"
        }]
      }
    ]
  }
}
```

## Built-in nástroje

| Nástroj | Popis | Kdy použít |
|---------|-------|------------|
| Bash | Shell příkazy | Systémové operace, git, build |
| Read | Čtení souborů | Analýza kódu, konfigurace |
| Edit | Editace souborů | Změny v kódu |
| Write | Nové soubory | Vytváření souborů |
| Grep | Vyhledávání obsahu | Hledání v kódu |
| Glob | Vyhledávání souborů | Pattern matching |
| WebSearch | Web search | Aktuální informace |
| WebFetch | Fetch URL | Stahování obsahu |
| Agent | Sub-agenti | Paralelní úkoly |

## Best Practices

1. **CLAUDE.md** by měl obsahovat projektové konvence, ne celou dokumentaci
2. **Skills** používejte pro opakované úkoly specifické pro projekt
3. **MCP servery** pro přístup k externím systémům (Azure, M365, DB)
4. **Hooks** pro audit, compliance, automatizace
5. **settings.local.json** pro osobní klíče a konfigurace (gitignored)

## M365/Azure workflow

```bash
# 1. Nainstalovat Azure CLI
az login

# 2. Přidat MCP servery do .claude/settings.json
# 3. Vytvořit skill pro typické Azure operace
# 4. Používat Claude Code pro:
#    - Infrastructure as Code (Bicep/Terraform)
#    - Azure DevOps pipeline YAML
#    - Graph API queries
#    - Azure Function development
```

## Doporučené MCP servery pro Claude Code

| Server | Účel | Install |
|--------|------|---------|
| Memory | Knowledge graph, persistent context | `npx @modelcontextprotocol/server-memory` |
| Filesystem | Bezpečný file access | `npx @modelcontextprotocol/server-filesystem` |
| Azure DevOps | Work items, repos, pipelines | microsoft/azure-devops-mcp |
| MS Docs | Oficiální MS dokumentace | MicrosoftDocs/mcp |
| Git | Git operace | `uvx mcp-server-git` |
| Sequential Thinking | Strukturované myšlení | `npx @modelcontextprotocol/server-sequential-thinking` |

## Agent SDK Patterns

### Basic Agent Loop
```python
from anthropic import Anthropic

client = Anthropic()

def agent_loop(system_prompt, tools, user_message):
    messages = [{"role": "user", "content": user_message}]
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            system=system_prompt,
            tools=tools,
            max_tokens=4096,
            messages=messages
        )
        # Process tool_use blocks
        if response.stop_reason == "tool_use":
            tool_results = execute_tools(response.content)
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            return response.content
```

### Multi-Agent Orchestration
```python
# Chief of Staff pattern - coordinator delegates to specialists
coordinator = Agent(name="coordinator", system="Route tasks to specialists")
researcher = Agent(name="researcher", system="Deep research with web search")
coder = Agent(name="coder", system="Write and review code")

# Each agent has its own tool set and MCP servers
researcher.mcp_servers = ["fetch", "memory"]
coder.mcp_servers = ["filesystem", "git"]
```

### Extended Thinking
```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    thinking={"type": "enabled", "budget_tokens": 5000},
    max_tokens=8096,
    messages=[{"role": "user", "content": "Complex analysis..."}]
)
# Access thinking: response.content[0] (thinking block)
# Access answer: response.content[1] (text block)
```

## Plugin Architecture (z anthropic repos)

### Plugin manifest (.claude-plugin/plugin.json)
```json
{
  "name": "azure-operations",
  "version": "1.0.0",
  "description": "Azure resource management plugin",
  "skills": ["skills/"],
  "commands": ["commands/"],
  "mcp": ".mcp.json",
  "hooks": ["hooks/"]
}
```

### Plugin structure
```
my-plugin/
├── .claude-plugin/plugin.json    # Manifest
├── commands/                      # Slash commands (/deploy, /status)
├── skills/                        # Auto-triggered skills
├── .mcp.json                      # MCP server connections
└── hooks/                         # Event-driven automation
```

### MCP Builder Skill (4 fáze)
1. **Research & Planning** - Pochopte API, definujte tool naming (e.g. `github_create_issue`)
2. **Implementation** - Zod/Pydantic schemas, annotations (`readOnlyHint`, `destructiveHint`)
3. **Review & Test** - Type coverage, build verification
4. **Deployment** - Publish, version, monitor

```python
# Python MCP Server s FastMCP
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("my_service")

class SearchInput(BaseModel):
    query: str = Field(..., description="Search query", min_length=1)
    limit: int = Field(default=10, ge=1, le=100)

@mcp.tool(
    name="search_documents",
    annotations={"readOnlyHint": True, "idempotentHint": True}
)
async def search(params: SearchInput) -> str:
    results = await do_search(params.query, params.limit)
    return json.dumps(results)
```

## Doporučené skill balíčky

### Microsoft Agent Skills (133 skills)
```bash
# Instalace přes npx
npx skills add microsoft/skills

# Nebo manuálně
git clone https://github.com/microsoft/skills.git
cp -r skills/.github/skills/ .claude/skills/
```
Kategorie: Foundry, Data, Messaging, Monitoring, Identity, Security, Integration.
Jazyky: Python (41), .NET (29), TypeScript (25), Java (26).

### MicrosoftDocs Agent Skills (193 Azure skills)
```bash
git clone https://github.com/MicrosoftDocs/Agent-Skills.git
cp -r Agent-Skills/skills/ .claude/skills/
```
9 kategorií: Compute, Integration, Data, AI/ML, Security, Networking, Infrastructure, Management, Specialized.

### Anthropic Skills (17 reference skills)
```bash
git clone https://github.com/anthropics/skills.git
# Skills: MCP builder, document skills (docx, pdf, pptx, xlsx), creative, enterprise
```

## Zdroje

- [anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook) - Příklady a patterns
- [microsoft/skills](https://github.com/microsoft/skills) - Microsoft agent skills
- [sickn33/antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills) - 1273+ community skills
