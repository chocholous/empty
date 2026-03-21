# MCP Servery - Katalog skills

## Co je MCP

Model Context Protocol (MCP) je otevřený protokol pro propojení AI nástrojů s externími systémy.
Definuje 3 primitivy: **Resources** (data), **Tools** (akce), **Prompts** (šablony).

## Oficiální MCP Servery

### Filesystem Server
- **Package:** `@modelcontextprotocol/server-filesystem`
- **Jazyk:** TypeScript
- **Skills:** read_text_file, read_media_file, write_file, edit_file, create_directory, list_directory, move_file, search_files, directory_tree, get_file_info
- **Konfigurace:** Povolené adresáře jako argumenty nebo přes MCP Roots protocol
- **Použití:** Bezpečné souborové operace s access control
- **Deploy:** `npx @modelcontextprotocol/server-filesystem /path/to/allowed/dir`

### Git Server
- **Package:** `mcp-server-git`
- **Jazyk:** Python
- **Skills:** git_status, git_diff_unstaged, git_diff_staged, git_commit, git_add, git_reset, git_log, git_create_branch, git_checkout, git_show
- **Konfigurace:** `--repository /path/to/repo`
- **Deploy:** `uvx mcp-server-git --repository /path`

### Fetch Server
- **Package:** `mcp-server-fetch`
- **Jazyk:** Python
- **Skills:** fetch (URL → markdown, s paginací přes start_index)
- **Konfigurace:** `--ignore-robots-txt`, `--user-agent`, `--proxy-url`
- **Deploy:** `uvx mcp-server-fetch`

### Memory Server (Knowledge Graph)
- **Package:** `@modelcontextprotocol/server-memory`
- **Jazyk:** TypeScript
- **Skills:** create_entities, create_relations, add_observations, delete_entities, delete_relations, delete_observations, read_graph, search_nodes, open_nodes
- **Konfigurace:** `MEMORY_FILE_PATH` env var
- **Formát:** JSONL backend, entity-relation-observation model
- **Deploy:** `npx @modelcontextprotocol/server-memory`
- **Relevance:** Ideální pro budování knowledge graphu!

### Time Server
- **Package:** `mcp-server-time`
- **Skills:** get_current_time, convert_time
- **Deploy:** `uvx mcp-server-time`

### Sequential Thinking Server
- **Package:** `@modelcontextprotocol/server-sequential-thinking`
- **Skills:** sequential_thinking (strukturované myšlení, revize, větvení)
- **Deploy:** `npx @modelcontextprotocol/server-sequential-thinking`

## Microsoft / Azure MCP Servery

### Microsoft MCP Catalog (2.8k stars) ⭐ HIGH
- **Repo:** [microsoft/mcp](https://github.com/microsoft/mcp)
- **Popis:** Oficiální katalog Microsoft MCP serverů
- **Pokrytí:** Azure services, M365, Graph API
- **Stav:** Aktivně vyvíjený, Microsoft-backed

### Azure DevOps MCP Server (1.4k stars) ⭐ HIGH
- **Skills:** Projects, repositories, work items, builds, wikis, pipelines
- **Jazyk:** TypeScript
- **Licence:** MIT
- **Architektura:** Tenká abstrakce nad REST APIs, jednoduché fokusované nástroje
- **Stav:** Aktivně vyvíjený, velká komunita

### Lokka M365 MCP (229 stars) ⭐ MEDIUM
- **Licence:** MIT
- **Popis:** Community MCP server pro Microsoft 365
- **Stav:** Aktivní vývoj

### CLI for M365 MCP (88 stars) ⭐ MEDIUM
- **Licence:** MIT
- **Skills:** Natural language management Microsoft 365
- **Pokrytí:** SharePoint, OneDrive, email, calendar, Teams
- **Stav:** 63 commitů, aktivní

### Microsoft EnterpriseMCP (37 stars) ⭐ LOW
- **Licence:** CC-BY-4.0
- **Popis:** MCP Server for Enterprise
- **Stav:** Raný vývoj

### m365-copilot-mcp (5 stars) ⭐ LOW
- **Licence:** MIT
- **Skills:** SharePoint, OneDrive, email, calendar, Teams meetings queries
- **Tools:** retrieval, chat, meeting insights, semantic search, file-based chat
- **Stav:** Nový, minimální adopce

## MCP Server pro budování (FastMCP pattern)

### TypeScript MCP Server
```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "my-server", version: "1.0.0" });

server.tool(
  "search_docs",
  { query: z.string(), limit: z.number().optional().default(10) },
  async ({ query, limit }) => ({
    content: [{ type: "text", text: JSON.stringify(await search(query, limit)) }]
  })
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

### Python MCP Server (FastMCP)
```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("my_service")

class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, ge=1, le=100)

@mcp.tool(name="search_docs", annotations={"readOnlyHint": True})
async def search(params: SearchInput) -> str:
    return json.dumps(await do_search(params.query, params.limit))
```

### Tool Annotations
| Annotation | Popis |
|-----------|-------|
| `readOnlyHint` | Tool nemění data |
| `destructiveHint` | Tool může smazat data |
| `idempotentHint` | Bezpečné opakované volání |
| `openWorldHint` | Interaguje s externím světem |

## Microsoft Azure MCP (200+ nástrojů, 40+ služeb)

Oficiální Azure MCP Server pokrývá:
- **Storage:** Blob, Queue, Table, Data Lake
- **Databases:** Cosmos DB, PostgreSQL, SQL, Redis
- **AI:** AI Search, OpenAI, AI Foundry, Content Safety
- **Compute:** App Service, Container Apps, Functions, AKS
- **DevOps:** Azure DevOps (work items, repos, pipelines, builds, wikis)
- **Identity:** Entra ID, Key Vault, RBAC
- **Monitoring:** Monitor, Application Insights, Log Analytics
- **Networking:** DNS, CDN, Front Door, Application Gateway

```bash
# Instalace
npx -y @azure/mcp@latest server start

# Auth: Azure CLI (az login) nebo DefaultAzureCredential
```

### Azure Skills deployment chain
```
azure-prepare → azure-validate → azure-deploy
```
Každá fáze vytváří artefakty: plan.md, validation results, deployment logs.

## Gemini MCP & Skills

### Gemini Skills (z google/gemini-skills)
```bash
# Instalace Gemini skills
git clone https://github.com/google/gemini-skills.git
# Key skills: gemini-api-dev, gemini-interactions-api, gemini-live-api-dev, vertex-ai-api-dev
```

### Gemini Interactions API (doporučená pro agenty)
- Server-side state management (konverzační historie na serveru)
- Background execution pro long-running tasks
- Built-in agents: Deep Research
- Remote MCP tool support

```python
from google import genai
client = genai.Client()

# Stateful conversation
interaction1 = client.interactions.create(
    model="gemini-3-flash-preview",
    input="Hi, my name is Phil."
)
interaction2 = client.interactions.create(
    model="gemini-3-flash-preview",
    input="What is my name?",
    previous_interaction_id=interaction1.id
)
# Server remembers: "Your name is Phil."
```

## MCP Konfigurace podle platformy

### Claude Desktop (claude_desktop_config.json)
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": { "MEMORY_FILE_PATH": "/Users/me/.claude-memory.jsonl" }
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "/Users/me/projects/myrepo"]
    }
  }
}
```

### Claude Code (.claude/settings.json)
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

### Cursor (settings)
V Cursor Settings → MCP → Add Server → konfigurovat command + args.

## MCP Protocol - Klíčové koncepty

| Primitiv | Řízení | Popis |
|----------|--------|-------|
| Resources | Aplikace | Data endpointy (soubory, DB schémata, konfigurace) |
| Tools | Model | Akce které model může zavolat (s user approval) |
| Prompts | Uživatel | Šablony a slash commands |

### Transporty
- **stdio** - Lokální procesy (Claude Desktop, Claude Code)
- **Streamable HTTP** - Vzdálené servery (POST + SSE)
- **SSE** - Legacy, pro polling

### Bezpečnost
- Explicitní user consent pro přístup k datům a spouštění nástrojů
- Servery nevidí data jiných serverů (izolace)
- Tool descriptions jsou nedůvěryhodné pokud server není trusted
