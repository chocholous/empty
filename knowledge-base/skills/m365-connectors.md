# M365 / Azure Skills & Connectors

## Přehled ekosystému

Microsoft 365 a Azure nabízí skills/connectors napříč několika platformami:

| Platforma | Mechanismus skills | M365 pokrytí |
|-----------|-------------------|--------------|
| Semantic Kernel | @kernel_function plugins + Copilot Agent Plugins | Email, Calendar, Drive, Tasks, Org, full Graph |
| Power Platform | 1,300+ connectors, 12,000+ actions | Kompletní M365 + Azure |
| Copilot Studio | Topics + Actions + Generative orchestration | M365 přes Power Platform + Graph |
| MCP Servers | Tools (10 official Microsoft MCP servers) | Azure 40+, M365, DevOps, Teams, SQL, Sentinel |
| GPT Actions | OpenAPI schemas | Přes Azure Functions middleware |
| Copilot Connectors | Synced (indexace) + Federated (real-time MCP) | 100+ pro Azure, Confluence, SF, SNow |

## Semantic Kernel M365 Plugins (.NET)

Nejkompletnější nativní integrace s M365 v AI frameworku.

### EmailPlugin (Plugins.MsGraph)
```csharp
// Skills: SendEmail, GetEmails, SearchEmails
var emailPlugin = new EmailPlugin(new OutlookMailConnector(graphClient));
kernel.Plugins.Add(emailPlugin);
```
- **Connector:** OutlookMailConnector
- **Modely:** EmailMessage, EmailAddress
- **Operace:** Send, read, search emails

### CalendarPlugin
```csharp
var calendarPlugin = new CalendarPlugin(new OutlookCalendarConnector(graphClient));
```
- **Operace:** Create, update, query events
- **Model:** CalendarEvent

### CloudDrivePlugin
- **Connector:** OneDrive/SharePoint
- **Operace:** Upload, download, list, search files

### TaskListPlugin
- **Connector:** Microsoft ToDo
- **Modely:** TaskManagementTask, TaskManagementTaskList
- **Operace:** Create, update, organize tasks

### OrganizationHierarchyPlugin
- **Connector:** Azure AD / Entra ID
- **Operace:** Org structure queries

### Autentizace
- MSAL-based (LocalUserMSALCredentialManager)
- Azure AD / Entra ID token-based
- Delegated permissions support
- Interactive a non-interactive flows

## Power Platform Connectors (Copilot Studio)

Power Platform má 1000+ connectorů. Klíčové pro M365:

**Pozor:** Jediný Premium connector upgraduje licenční požadavek celé aplikace pro všechny uživatele.

### Standard Connectors (zahrnuty v M365 licenci)
| Connector | Klíčové capabilities | Limity |
|-----------|---------------------|--------|
| **SharePoint** | Lists CRUD, document libraries, triggers on changes | 600 actions/min throttle |
| **Outlook 365** | Send/manage emails, calendar, contacts, meeting scheduling | |
| **Microsoft Teams** | Post messages, channels, adaptive cards | |
| **OneDrive Business** | File CRUD, sharing, folder management | |
| **Excel Online** | Tables, worksheets, ranges, calculations | |
| **Planner** | Tasks, buckets, plans, assignments | |
| **Microsoft To Do** | Personal tasks, lists | |
| **OneNote** | Notebooks, pages, sections | |
| **Forms** | Create/read forms, responses | |

### Premium Connectors
| Connector | Klíčové capabilities |
|-----------|---------------------|
| **Azure DevOps** | Work items, builds, releases, repos, pipelines |
| **Dataverse** | Full entity CRUD, business logic, relationships |
| **SQL Server** | Direct database integration |
| **Azure Blob Storage** | Blob CRUD, containers |
| **Azure SQL** | Queries, stored procedures |
| **Dynamics 365** | CRM entities, business processes |
| **Azure Key Vault** | Secrets read |
| **Azure AI Services** | Cognitive services (vision, language, speech) |
| **Microsoft Graph** (HTTP) | Univerzální API pro celé M365 |

### Custom Connectors
- OpenAPI/Swagger definice pro vlastní API
- Azure Functions jako middleware
- Logic Apps jako orchestrace
- Source code: [microsoft/PowerPlatformConnectors](https://github.com/microsoft/PowerPlatformConnectors)

### Copilot Connectors (dříve Graph Connectors)
- **Synced:** Indexace externích dat do Microsoft Graph (100+ connectors)
- **Federated** (preview): Real-time retrieval přes MCP bez indexování
- Pro: Azure services, Confluence, Salesforce, ServiceNow...

## Microsoft Graph API jako skill source

Microsoft Graph je **univerzální API** pro M365. Pokrytí:

### Dostupné operace
- **Users** - Profily, org hierarchie, skupiny
- **Mail** - Zprávy, složky, pravidla, flagy
- **Calendar** - Události, volné termíny, pokoje
- **Files** - OneDrive, SharePoint, sharing
- **Teams** - Kanály, zprávy, schůzky, tabs
- **Planner** - Úkoly, plány, buckety
- **Todo** - Osobní úkoly
- **OneNote** - Notebooks, stránky, sekce
- **Security** - Alerts, incidents
- **Search** - Unified search across M365

### Použití v různých platformách

#### V Semantic Kernel (Copilot Agent Plugins)
```csharp
// SK může importovat Graph API jako plugin z OpenAPI spec
// Kiota CLI generuje Copilot Agent Plugins z Graph OpenAPI specs
await kernel.ImportPluginFromCopilotAgentPluginAsync("graph-mail", manifestUri);
```
Nové: **Retrieval API** (Build 2025) umožňuje query přímo do Microsoft semantic indexu - eliminuje potřebu vlastních vector stores.

#### V GPT Actions (přes Azure Functions)
```python
# Azure Function jako middleware
import azure.functions as func
from msgraph import GraphServiceClient

@app.route(route="graph-proxy")
async def graph_proxy(req: func.HttpRequest):
    client = GraphServiceClient(credential)
    result = await client.users.get()
    return func.HttpResponse(json.dumps(result))
```

#### V MCP serverech
CLI for M365 MCP a Lokka wrappují Graph API do MCP tools.

## Azure AI Skills

### Azure AI Search Skillsets (~19 built-in skills)

| Kategorie | Skills | Billing |
|-----------|--------|---------|
| **NLP** | Entity Recognition v3, Sentiment, PII Detection, Key Phrase Extraction, Language Detection, Text Translation, Custom Entity Lookup | Billable (Foundry) |
| **Vision** | OCR (printed + handwritten), Image Analysis (faces, landmarks) | Billable (Foundry) |
| **Chunking & Vectors** | Text Split (pages/sentences), Azure OpenAI Embedding, Document Layout | Mixed |
| **Utility** | Conditional, Document Extraction, Shaper, Text Merge | **Free** |
| **Azure-Hosted** | AML Skill (Azure ML endpoint), Azure Content Understanding | Your resource |
| **Custom** | Custom Web API Skill (any REST endpoint) | Your infra |

Free tier: 20 dokumentů/indexer/den pro billable enrichments.
Docs: [Skills Reference](https://learn.microsoft.com/en-us/azure/search/cognitive-search-predefined-skills)

### Azure OpenAI Function Calling
```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://myendpoint.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-01"
)

tools = [{
    "type": "function",
    "function": {
        "name": "search_sharepoint",
        "description": "Search SharePoint documents",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "site": {"type": "string"}
            },
            "required": ["query"]
        }
    }
}]

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Find Q4 reports"}],
    tools=tools,
    tool_choice="auto"
)
```

## Doporučení pro výběr

| Scénář | Doporučení |
|--------|------------|
| Rychlý přístup k M365 z Claude/Cursor | CLI for M365 MCP server nebo Lokka |
| Enterprise integrace s M365 | Semantic Kernel + Graph plugins |
| Low-code automatizace | Copilot Studio + Power Platform connectors |
| Azure DevOps workflows | Azure DevOps MCP server (1.4k stars) |
| Custom M365 skills | Azure Functions + Graph API |
| RAG s firemními daty | Azure AI Search + Azure OpenAI |
