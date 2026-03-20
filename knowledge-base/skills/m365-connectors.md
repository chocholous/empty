# M365 / Azure Skills & Connectors

## Přehled ekosystému

Microsoft 365 a Azure nabízí skills/connectors napříč několika platformami:

| Platforma | Mechanismus skills | M365 pokrytí |
|-----------|-------------------|--------------|
| Semantic Kernel | @kernel_function plugins | Email, Calendar, Drive, Tasks, Org |
| Power Platform | Connectors (1000+) | Kompletní M365 + Azure |
| Copilot Studio | Topics + Actions + Connectors | M365 přes Power Platform |
| MCP Servers | Tools | Záleží na serveru |
| GPT Actions | OpenAPI schemas | Přes Azure Functions middleware |

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

### Standard Connectors (zdarma)
- **SharePoint** - Lists, documents, sites, permissions
- **Outlook 365** - Email, calendar, contacts
- **Microsoft Teams** - Messages, channels, meetings
- **OneDrive for Business** - Files, folders, sharing
- **Excel Online** - Tables, worksheets, ranges
- **Planner** - Tasks, buckets, plans
- **Microsoft To Do** - Tasks, lists

### Premium Connectors
- **Azure DevOps** - Work items, repos, pipelines, builds
- **Azure Blob Storage** - Blobs, containers
- **Azure SQL** - Queries, stored procedures
- **Dynamics 365** - CRM entities, business processes
- **Azure Key Vault** - Secrets management
- **Azure AI Services** - Cognitive services (vision, language, speech)
- **Microsoft Graph** - Univerzální API pro celé M365

### Custom Connectors
- OpenAPI/Swagger definice pro vlastní API
- Azure Functions jako middleware
- Logic Apps jako orchestrace

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

#### V Semantic Kernel
```python
# SK automaticky generuje funkce z Graph API
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
# Plugin wraps Graph API calls as kernel functions
```

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

### Azure AI Search Skillsets
Built-in cognitive skills pro enrichment:
- **Entity Recognition** - Rozpoznání osob, míst, organizací
- **Key Phrase Extraction** - Klíčová slova z textu
- **Language Detection** - Detekce jazyka
- **Sentiment Analysis** - Analýza sentimentu
- **OCR** - Text z obrázků
- **Image Analysis** - Popis obrázků, tagy
- **Custom Skills** - Azure Functions webhooks

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
