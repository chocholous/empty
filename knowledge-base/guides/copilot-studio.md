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

## Power Platform Connectors

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

## Zdroje

- [microsoft/skills](https://github.com/microsoft/skills) - Microsoft skills včetně Copilot Studio
- [Power Platform Connectors](https://learn.microsoft.com/connectors/connector-reference/) - 1000+ connectors
- [microsoft/mcp](https://github.com/microsoft/mcp) - M365 Agents Toolkit MCP
