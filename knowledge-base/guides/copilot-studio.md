# Copilot Studio - Kompletní průvodce

## Co je Copilot Studio

Microsoft low-code platforma pro budování AI agentů a copilotů.
Integruje se s M365, Power Platform, Teams, a vlastními systémy.

## Skills v Copilot Studio

### Topics (hlavní skill mechanismus)
Topics jsou konverzační flow-based skills:
- **Trigger phrases** - Kdy se topic aktivuje
- **Nodes** - Kroky konverzace (Message, Question, Action, Condition)
- **Actions** - Volání connectorů a API
- **Variables** - Kontext a data

### Pre-built topics
- Greeting, Goodbye, Escalate
- Thank you, Start over
- Conversational boosting (Generative AI)

### Generative AI orchestrace
Copilot Studio může automaticky routovat mezi topics pomocí AI:
- Popis topiců stačí jako "skill description"
- AI vybírá relevantní topic podle user query
- Kombinace s Generative Answers pro fallback

## M365 Copilot Extensibility

### Způsoby rozšíření M365 Copilot

| Přístup | Popis | Nástroj |
|---------|-------|---------|
| **Declarative agents** | Custom instructions + knowledge + actions na M365 orchestrátoru | JSON manifest + Copilot Studio / Teams Toolkit |
| **API plugins** | REST API integrace přes OpenAPI | OpenAPI spec + manifest |
| **MCP plugins** | MCP servery jako tool providers | MCP protocol |
| **Copilot connectors** | Indexace externích dat do Microsoft Graph | Graph connector SDK |
| **Office JS plugins** (preview) | Read/write Office dokument z Copilota | Office JavaScript Library |

### Declarative Agents (production-ready)
- Customizace M365 Copilot s vlastními instrukcemi, knowledge a actions
- Běží na stejném orchestrátoru jako M365 Copilot
- Max 5 always-injected plugins, pak semantic matching
- Schema v1.5 přidává meeting search

### Key 2025+ novinky
- **M365 Copilot Tuning** - low-code model tuning s firemními daty
- **Multi-agent orchestration** - agenti z M365, Azure AI a Fabric spolupracují
- **Microsoft Agent Factory** - build + deploy s jedním metered plánem
- **Computer use** v Copilot Studio agentech
- **Federated connectors** (preview) - real-time retrieval přes MCP bez indexování

## Power Platform Connectors

1,400+ systémů. Typy:
- **Power Platform connectors** - Real-time API calls (read/write)
- **Copilot connectors** (dříve Graph connectors) - Indexace do M365 Graph (40+ GA)
- **Custom connectors** - Vlastní REST/SOAP API
- **Federated connectors** (preview) - Real-time retrieval přes MCP

### Standard (zdarma s licencí)
| Connector | Skills |
|-----------|--------|
| **SharePoint** | Lists CRUD, document libraries, site info, permissions |
| **Outlook 365** | Send/read email, calendar events, contacts |
| **Teams** | Post messages, create channels, schedule meetings |
| **OneDrive Business** | Upload/download files, folders, sharing |
| **Excel Online** | Tables, worksheets, ranges, calculations |
| **Planner** | Tasks, buckets, plans, assignments |
| **Microsoft To Do** | Personal tasks, lists |
| **OneNote** | Notebooks, pages, sections |
| **Forms** | Create/read forms, responses |

### Premium
| Connector | Skills |
|-----------|--------|
| **Azure DevOps** | Work items, repos, pipelines, builds, releases |
| **Azure Blob Storage** | Blob CRUD, containers |
| **Azure SQL** | Queries, stored procedures |
| **Microsoft Graph** | Univerzální M365 API (users, groups, apps) |
| **Dynamics 365** | CRM entities, business processes |
| **Azure Key Vault** | Secrets read |
| **Azure AI Services** | Vision, language, speech |
| **Dataverse** | Tables, rows, actions |

### Custom Connectors
```yaml
# OpenAPI/Swagger definice pro vlastní API
openapi: 3.0.0
info:
  title: My Custom API
paths:
  /search:
    post:
      operationId: searchDocuments
      parameters:
        - name: query
          in: query
          required: true
          schema:
            type: string
```

## Agent Building

### Declarative Agents (M365 Copilot)
```json
{
  "name": "IT Help Desk",
  "description": "Handles IT support requests",
  "instructions": "You are an IT support agent...",
  "capabilities": {
    "plugins": ["sharepoint-search", "servicenow-tickets"],
    "graphConnectors": ["IT Knowledge Base"]
  }
}
```

### Copilot Studio + Semantic Kernel
SK má CopilotStudioAgent pro programatický přístup:
```python
from semantic_kernel.agents import CopilotStudioAgent

agent = CopilotStudioAgent(
    name="ITSupport",
    endpoint="https://...",
    # Využívá existující Copilot Studio bot
)
```

## M365 Agents Toolkit

Z [microsoft/mcp](https://github.com/microsoft/mcp):
- MCP server pro M365 Agents Toolkit
- Propojení AI agentů s M365 + Copilot
- Build apps a agents pro Microsoft 365

## Workflow příklady

### IT Support Bot
```
1. Topic: "Password Reset"
   → Action: Graph API → reset password
   → Message: confirmation

2. Topic: "Software Request"
   → Action: ServiceNow connector → create ticket
   → Action: Teams → notify approver
   → Message: ticket number

3. Generative Answers: fallback na IT knowledge base
```

### Sales Assistant
```
1. Topic: "Customer Info"
   → Action: Dynamics 365 → customer lookup
   → Action: SharePoint → recent proposals
   → Message: customer summary

2. Topic: "Create Proposal"
   → Action: OneDrive → copy template
   → Action: Dynamics 365 → populate data
   → Message: proposal link
```

## Best Practices

1. **Generative AI orchestrace** - Popište topics jasně, AI routuje automaticky
2. **Connectors** - Používejte standard kde to jde, premium jen když nutné
3. **Custom connectors** - Pro interní API, OpenAPI spec
4. **Testing** - Používejte Test canvas před publikací
5. **Analytics** - Sledujte topic completion rate a customer satisfaction
6. **Security** - DLP policies, authentication pro connectors

## MCP v Copilot Studio

### MCP Integration Pattern
1. Vytvořit MCP server (TypeScript/Python)
2. Definovat tools a resources
3. Připojit jako Copilot Studio action
4. Předávat MCP resources jako agent inputs

```json
// Příklad MCP konfigurace pro Copilot Studio
{
  "connections": [
    {
      "name": "azure-search",
      "url": "https://my-mcp-server.azurewebsites.net/sse",
      "tools": ["search_documents", "get_document"]
    }
  ]
}
```

### A2A Protocol (Agent-to-Agent)
- Copilot Studio podporuje A2A pro multi-agent komunikaci
- Agent může delegovat na jiného agenta
- Příklad: HR agent → IT agent pro access provisioning

## Declarative Agents (M365 Copilot)

### Manifest (v1.2+)
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.2/schema.json",
  "version": "v1.2",
  "name": "IT Help Desk",
  "description": "Handles IT support requests",
  "instructions": "$[file('instruction.txt')]",
  "actions": [
    { "id": "action_1", "file": "ai-plugin.json" }
  ],
  "conversation_starters": [
    { "text": "How do I reset my password?" },
    { "text": "Request new software" }
  ]
}
```

### Teams Manifest Integration
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.25/MicrosoftTeams.schema.json",
  "manifestVersion": "1.25",
  "copilotAgents": {
    "declarativeAgents": [
      {
        "id": "declarativeAgent",
        "file": "declarativeAgent.json"
      }
    ]
  }
}
```

### TypeSpec pro generování pluginů
```yaml
# tspconfig.yaml
emit:
  - "@typespec/openapi3"
  - "@microsoft/typespec-m365-copilot"
options:
  "@typespec/openapi3":
    emitter-output-dir: "./appPackage/.generated/specs"
  "@microsoft/typespec-m365-copilot":
    emitter-output-dir: "./appPackage/.generated"
    output-file: declarativeAgent.json
```

## Contact Center Integration

Copilot Studio podporuje handoff do live agent systémů:
- **Salesforce Einstein** - Přímá integrace
- **ServiceNow Virtual Agent** - IT support handoff
- **Genesys** - Contact center handoff
- **Custom skill** - Vlastní handoff logika

### Handoff flow
```
1. Agent vede konverzaci
2. Při eskalaci předá kontext live agentovi
3. Live agent vidí historii + AI summary
4. Po vyřešení může vrátit zpět agentovi
```

## PnP Solutions (importovatelné)

Komunita nabízí hotové solutions k importu:
- **Account/Contact lookup** - CRM integrace
- **Language detection** - Auto-detect a překlad
- **Dataverse indexer** - Automatická indexace
- **Feedback analyzer** - Sentiment z feedbacku

Import: `make.powerapps.com → Solutions → Import → .zip`

## Build & Provision Workflow (m365agents.yml)
```yaml
version: v1.8
provision:
  - uses: teamsApp/create
    with:
      name: MyAgent${{APP_NAME_SUFFIX}}

  - uses: typeSpec/compile
    with:
      path: ./main.tsp
      manifestPath: ./appPackage/manifest.json

  - uses: oauth/register
    with:
      name: MyAPIAuth
      appId: ${{TEAMS_APP_ID}}
      flow: authorizationCode

  - uses: apiKey/register
    with:
      name: ApiKeyAuth
      appId: ${{TEAMS_APP_ID}}
```

## Zdroje

- [microsoft/skills](https://github.com/microsoft/skills) - Microsoft skills včetně Copilot Studio
- [Power Platform Connectors](https://learn.microsoft.com/connectors/connector-reference/) - 1000+ connectors
- [microsoft/mcp](https://github.com/microsoft/mcp) - M365 Agents Toolkit MCP
