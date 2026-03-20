# Claude Desktop - Kompletní průvodce

## Co je Claude Desktop

Desktopová aplikace Anthropic pro Claude. Hlavní výhoda: nativní podpora MCP serverů.

## MCP konfigurace

### Config soubor
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"],
      "env": {}
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "/Users/me/.claude-memory.jsonl"
      }
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "/Users/me/projects/myrepo"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "ms-docs": {
      "command": "npx",
      "args": ["-y", "@microsoftdocs/mcp"]
    }
  }
}
```

### M365/Azure MCP servery pro Claude Desktop

#### Microsoft MCP Catalog
Z [microsoft/mcp](https://github.com/microsoft/mcp) - Azure MCP Server 1.0 (GA):
- 40+ Azure services
- M365 Tools: Calendar, Mail, Search, People, Admin
- AKS, Foundry, Clarity

```json
{
  "mcpServers": {
    "azure": {
      "command": "npx",
      "args": ["-y", "@microsoft/azure-mcp"],
      "env": {
        "AZURE_SUBSCRIPTION_ID": "your-sub-id"
      }
    },
    "azure-devops": {
      "command": "npx",
      "args": ["-y", "@microsoft/azure-devops-mcp"],
      "env": {
        "AZURE_DEVOPS_ORG": "your-org",
        "AZURE_DEVOPS_PAT": "your-pat"
      }
    }
  }
}
```

## Projekty

Claude Desktop podporuje Projects pro organizaci konverzací:
- Skupiny konverzací podle tématu/projektu
- Sdílené instrukce (Project Knowledge)
- Nahrávání souborů jako kontext

### Project Knowledge jako skills
```markdown
# Project Knowledge příklad

## Azure Infrastructure Rules
- Všechny resources v West Europe regionu
- Naming: {svc}-{env}-{region}-{nn} (e.g., app-prod-weu-01)
- Vždy managed identity, nikdy connection strings
- Tags: Environment, Owner, CostCenter povinné

## Deployment Process
1. PR review required
2. CI pipeline must pass
3. Staging deploy + smoke tests
4. Production deploy s approval gate
```

## Prompts přes MCP

MCP servery mohou poskytovat prompts (šablony):
```
# Pokud MCP server definuje prompt "analyze-code":
# Uživatel v Claude Desktop vidí jako slash command
```

## Workflow s M365

### Scénář: Analýza firemních dokumentů
1. Memory MCP → persistent knowledge graph
2. Filesystem MCP → přístup k lokálním souborům
3. Fetch MCP → stahování webového obsahu
4. MS Docs MCP → oficiální Azure dokumentace
5. Azure MCP → přímý přístup k Azure resources

### Scénář: Meeting prep
1. M365 Calendar tools → nadcházející schůzky
2. M365 Mail tools → relevantní emaily
3. Memory → kontext z předchozích konverzací
4. Sequential Thinking → strukturovaná příprava

## Best Practices

1. **Memory server** - Vždy mít zapnutý pro persistent kontext
2. **Filesystem** - Omezit na konkrétní adresáře (security)
3. **Kombinace serverů** - Memory + Filesystem + Fetch = silný základ
4. **Project Knowledge** - Pro projekt-specifické instrukce a pravidla
5. **M365 MCP** - Přidávat postupně podle potřeby

## Omezení

- Nemá přímý přístup ke kódu (na to je Claude Code)
- MCP servery musí běžet lokálně (stdio transport)
- Žádné hooks ani custom commands (na to je Claude Code)

## Zdroje

- [microsoft/mcp](https://github.com/microsoft/mcp) - Microsoft MCP servery
- [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) - Oficiální MCP servery
- [MicrosoftDocs/mcp](https://github.com/MicrosoftDocs/mcp) - MS Learn MCP
