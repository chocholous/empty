# Cursor IDE - Kompletní průvodce

## Co je Cursor

Fork VS Code s nativní AI integrací. Podporuje MCP, custom rules, a AI composer.

## Skills systém

### Cursor Rules (.cursor/rules/)
Cursor rules jsou ekvivalent skills - kontextové instrukce pro AI:

```markdown
<!-- .cursor/rules/azure.mdc -->
---
description: Azure development patterns and conventions
globs: ["**/azure/**", "**/infra/**", "**/*.bicep", "**/terraform/**"]
---
# Azure Development Rules

## Naming Conventions
- Resources: {svc}-{env}-{region}-{nn}
- Resource Groups: rg-{project}-{env}-{region}

## Security
- Always use Managed Identity
- Never hardcode connection strings
- Use Azure Key Vault for secrets

## IaC
- Bicep for Azure-native, Terraform for multi-cloud
- Modules for reusable components
- Parameters for environment-specific values
```

### Globální rules vs project rules
- **Globální:** `~/.cursor/rules/` - platí pro všechny projekty
- **Project:** `.cursor/rules/` - specifické pro projekt
- **Legacy:** `.cursorrules` v root (jednoduchý markdown soubor)

### Globs pattern matching
Rules se aktivují automaticky podle otevřených souborů:
```yaml
globs: ["**/*.py"]          # Python soubory
globs: ["**/azure/**"]      # Azure-related soubory
globs: ["**/*.bicep"]       # Bicep templates
globs: ["**/api/**"]        # API endpoints
```

## MCP v Cursoru

Cursor je **jeden z nejkompletnějších MCP klientů** - podporuje všech 5 protocol capabilities (tools, resources, prompts, elicitation, sampling).

### Feature timeline
- **June 2025:** OAuth support (v1.0)
- **August 2025:** Elicitation - servery mohou žádat user input (v1.5)
- **September 2025:** Resources support (v1.6)

### Konfigurace
- **GUI:** Settings → Tools & Integrations → New MCP Server
- **Project:** `.cursor/mcp.json`
- **Global:** `~/.cursor/mcp.json`

Transporty: stdio, SSE, Streamable HTTP.

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start"]
    },
    "azure-devops": {
      "command": "npx",
      "args": ["-y", "@azure-devops/mcp", "MyOrgName"]
    },
    "ms365": {
      "command": "npx",
      "args": ["-y", "@softeria/ms-365-mcp-server"],
      "env": {
        "MS365_MCP_CLIENT_ID": "${MS365_MCP_CLIENT_ID}",
        "MS365_MCP_TENANT_ID": "${MS365_MCP_TENANT_ID}"
      }
    },
    "ms-docs": {
      "command": "npx",
      "args": ["-y", "@microsoftdocs/mcp"]
    }
  }
}
```

### Praktické limity
- **Max ~40 aktivních tools** napříč všemi servery - za tím agent degraduje při výběru tool
- Vždy **pin npm verze** - CVE-2025-6514 byl critical command injection v `mcp-remote`
- Preferujte `DefaultAzureCredential` nad PATs

## AI Features

### Chat (Ctrl+L)
- Kontext-aware chat s přístupem k codebase
- @-mention soubory, funkce, docs
- MCP tools dostupné v chatu

### Composer (Ctrl+I)
- Multi-file editing
- AI navrhuje změny across files
- Review a apply changes

### Tab Completion
- Inline code suggestions
- Context-aware completions

### Terminal (Ctrl+K)
- AI-assisted terminal commands
- Vysvětlení chyb

## Workflow s M365/Azure

### Doporučené nastavení
```
.cursor/
├── rules/
│   ├── azure.mdc           # Azure konvence
│   ├── m365.mdc            # M365 API patterns
│   ├── security.mdc        # Security pravidla
│   └── testing.mdc         # Testing patterns
└── mcp.json                # MCP servery
```

### Příklad Azure rules
```markdown
<!-- .cursor/rules/m365.mdc -->
---
description: Microsoft 365 API patterns
globs: ["**/graph/**", "**/m365/**"]
---
# M365 Development

## Graph API
- Use Microsoft Graph SDK, not raw HTTP
- Always request minimum permissions (least privilege)
- Handle pagination with @odata.nextLink
- Use batch requests for multiple operations

## Authentication
- Use MSAL library
- Prefer interactive auth for dev, managed identity for prod
- Cache tokens with MSAL token cache
```

## Best Practices

1. **Rules** - Specifické globs pro přesný kontext
2. **MCP** - Přidat relevantní servery pro projekt
3. **Composer** - Pro multi-file changes, review before apply
4. **Chat** - Pro otázky a exploraci, @-mention soubory
5. **Rules ve verzi** - `.cursor/rules/` commitovat do repo

## Zdroje

- [microsoft/skills](https://github.com/microsoft/skills) - Skills kompatibilní s Cursor
- [sickn33/antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills) - 1273+ skills
- [microsoft/mcp](https://github.com/microsoft/mcp) - Microsoft MCP servery
