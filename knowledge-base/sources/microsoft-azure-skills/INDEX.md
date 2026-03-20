# Azure Skills Plugin - INDEX

> Plugin pro coding agenty (GitHub Copilot, Claude Code) obsahujici 22 SKILL.md definic pro Azure workflows, napojeny na Azure MCP Server (200+ tools, 40+ sluzeb) a Foundry MCP. Jeden install = Azure expertiza + live execution.

## Architektura pluginu

```
plugin.json                          # Plugin manifest (name, version, skills path, mcp config)
.mcp.json                           # MCP server konfigurace (Azure MCP + Context7)
.github/plugins/azure-skills/.mcp.json  # Alternativni MCP konfig pro GitHub Copilot
skills/                             # 22 SKILL.md definic s references
```

## Use case tabulka

### Priprava a deploy (hlavni workflow: prepare -> validate -> deploy)

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Pripravit app pro Azure (Bicep/Terraform/azure.yaml) | `skills/azure-prepare/SKILL.md` | Skill | MD |
| Reference pro analyze, scan, architecture | `skills/azure-prepare/references/` | Guides | MD |
| Recipe selection (AZD/AZCLI/Bicep/Terraform) | `skills/azure-prepare/references/recipe-selection.md` | Guide | MD |
| Plan template (.azure/plan.md) | `skills/azure-prepare/references/plan-template.md` | Template | MD |
| Security hardening reference | `skills/azure-prepare/references/security.md` | Guide | MD |
| Azure SDK references (Python/.NET/TS/Java) | `skills/azure-prepare/references/sdk/` | Guides | MD |
| Service-specific references | `skills/azure-prepare/references/services/` | Guides | MD |
| Validovat deployment pred spustenim | `skills/azure-validate/SKILL.md` | Skill | MD |
| Spustit deployment (azd up, terraform apply) | `skills/azure-deploy/SKILL.md` | Skill | MD |

### Diagnostika a monitoring

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Debug produkce (AppLens, Monitor, health) | `skills/azure-diagnostics/SKILL.md` | Skill | MD |
| AKS troubleshooting (pods, nodes, CoreDNS) | `skills/azure-diagnostics/aks-troubleshooting/` | Guide | MD |
| Application Insights instrumentace | `skills/appinsights-instrumentation/SKILL.md` | Skill | MD |
| AppInsights SDK priklady | `skills/appinsights-instrumentation/examples/` | Samples | - |
| AppInsights setup scripty | `skills/appinsights-instrumentation/scripts/` | Scripts | - |

### Optimalizace a compliance

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Najit usporami v Azure subscripci | `skills/azure-cost-optimization/SKILL.md` | Skill | MD |
| Cost optimization templates | `skills/azure-cost-optimization/templates/` | Templates | - |
| Compliance a security audit | `skills/azure-compliance/SKILL.md` | Skill | MD |
| Upgrade Azure service tier/SKU | `skills/azure-upgrade/SKILL.md` | Skill | MD |

### AI a Foundry

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Azure AI (Search, Speech, OpenAI, DocIntelligence) | `skills/azure-ai/SKILL.md` | Skill | MD |
| API Management jako AI Gateway | `skills/azure-aigateway/SKILL.md` | Skill | MD |
| Microsoft Foundry (agents, modely, eval) | `skills/microsoft-foundry/SKILL.md` | Skill | MD |
| Deploy model do Foundry | `skills/microsoft-foundry/models/deploy-model/SKILL.md` | Sub-skill | MD |
| Deploy model - preset varianta | `skills/microsoft-foundry/models/deploy-model/preset/SKILL.md` | Sub-skill | MD |
| Deploy model - custom varianta | `skills/microsoft-foundry/models/deploy-model/customize/SKILL.md` | Sub-skill | MD |
| Deploy model - capacity discovery | `skills/microsoft-foundry/models/deploy-model/capacity/SKILL.md` | Sub-skill | MD |
| Foundry agent workflows | `skills/microsoft-foundry/foundry-agent/` | Guide | MD |
| Foundry project management | `skills/microsoft-foundry/project/` | Guide | MD |
| Foundry RBAC a permissions | `skills/microsoft-foundry/rbac/` | Guide | MD |
| Foundry quota a capacity | `skills/microsoft-foundry/quota/` | Guide | MD |
| Foundry resource provisioning | `skills/microsoft-foundry/resource/` | Guide | MD |

### Infrastruktura a resources

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Doporucit VM size podle workloadu | `skills/azure-compute/SKILL.md` | Skill | MD |
| Azure Storage (Blob, Files, Queue, Table) | `skills/azure-storage/SKILL.md` | Skill | MD |
| Azure messaging (Event Hubs, Service Bus) | `skills/azure-messaging/SKILL.md` | Skill | MD |
| KQL dotazy v Azure Data Explorer | `skills/azure-kusto/SKILL.md` | Skill | MD |

### Identita a pristup

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| RBAC role assignment (least privilege) | `skills/azure-rbac/SKILL.md` | Skill | MD |
| Entra ID app registration + OAuth | `skills/entra-app-registration/SKILL.md` | Skill | MD |

### Resource management

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Najit a vypsat Azure resources | `skills/azure-resource-lookup/SKILL.md` | Skill | MD |
| Vizualizovat resources (Mermaid diagram) | `skills/azure-resource-visualizer/SKILL.md` | Skill | MD |
| Zkontrolovat quotas a usage | `skills/azure-quotas/SKILL.md` | Skill | MD |

### Migrace

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Migrace z AWS/GCP do Azure | `skills/azure-cloud-migrate/SKILL.md` | Skill | MD |
| Copilot SDK app na Azure | `skills/azure-hosted-copilot-sdk/SKILL.md` | Skill | MD |

### MCP Server konfigurace

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| MCP config (Azure + Context7) | `.mcp.json` | Config | JSON |
| MCP config pro GitHub Copilot plugin | `.github/plugins/azure-skills/.mcp.json` | Config | JSON |
| Plugin manifest | `plugin.json` | Config | JSON |

## Key patterns

### Hlavni deployment workflow (chain)
Skills jsou navrzeny pro sekvencni pouziti:

```
azure-prepare  -->  azure-validate  -->  azure-deploy
   (plan.md)        (preflight)         (azd up / terraform apply)
```

1. `azure-prepare` vytvori `.azure/plan.md` + infrastrukturu (Bicep/Terraform)
2. `azure-validate` provede preflight kontroly
3. `azure-deploy` spusti deployment

### Specialized routing (z azure-prepare)
Nektera klicova slova spusti specializovany skill PRED azure-prepare:

| Trigger | Skill |
|---------|-------|
| AWS Lambda, migrate AWS/GCP | `azure-cloud-migrate` |
| Copilot SDK, CopilotClient | `azure-hosted-copilot-sdk` |
| AI gateway, APIM AI | `azure-aigateway` |

### SKILL.md format
Kazdy skill ma:
- **YAML front matter**: name, description (s trigger keywords), license, metadata
- **Triggers**: kdy skill aktivovat
- **Rules**: zavazna pravidla pro agenta
- **Phases**: kroky k provedeni
- **References**: podrobne navody v `references/` podadresari

### MCP Server setup
```json
{
  "mcpServers": {
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start"]
    }
  }
}
```

### Instalace pluginu
- **GitHub Copilot CLI**: `/plugin marketplace add microsoft/azure-skills` + `/plugin install azure@azure-skills`
- **VS Code**: Azure MCP extension z Marketplace
- **Claude Code**: `/plugin marketplace add microsoft/azure-skills` + `/plugin install azure@azure-skills`

## Prerequisites

- Azure account/subscription
- **Node.js 18+** (pro `npx` MCP server)
- **Azure CLI** (`az login`) - autentizace
- **Azure Developer CLI** (`azd auth login`) - pro deployment workflows
- Volitelne: service principal credentials (AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
