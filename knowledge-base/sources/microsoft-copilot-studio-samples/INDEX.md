# Copilot Studio Samples - INDEX

> Oficialni Microsoft repozitar s ukazkami pro Copilot Studio: MCP integrace, A2A protokol, SSO, testovani, custom UI, contact center handoff a importovatelne Power Platform solutions.

## Use case tabulka

### Extensibility - MCP, A2A, Agents SDK

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| MCP server integrace - prehled | `extensibility/mcp/README.md` | Guide | MD |
| Predavani MCP resources jako vstupu agenta | `extensibility/mcp/pass-resources-as-inputs/README.md` | Sample | - |
| MCP server pro vyhledavani (TypeScript) | `extensibility/mcp/search-species-resources-typescript/README.md` | Sample | TypeScript |
| A2A protokol - prehled | `extensibility/a2a/README.md` | Guide | MD |
| Zakladni A2A implementace | `extensibility/a2a/Simple-A2A-Sample/README.md` | Sample | - |
| Agents SDK - prehled | `extensibility/agents-sdk/README.md` | Guide | MD |
| Azure Function connector pro volani agentu | `extensibility/agents-sdk/call-agent-connector/README.md` | Sample | - |
| Multilingvalni bot s automatickym prekladem | `extensibility/agents-sdk/multilingual-bot/README.md` | Sample | - |
| Relay bot pattern | `extensibility/agents-sdk/relay-bot/README.md` | Sample | - |
| Copilot Studio klient (konzolova app) | `extensibility/agents-sdk/copilotstudio-client/README.md` | Sample | .NET/Node/Python |
| Copilot Studio skill (echo bot) | `extensibility/agents-sdk/copilotstudio-skill/README.md` | Sample | .NET/Node/Python |
| Multi-agent v jednom hostu | `extensibility/agents-sdk/multiagent/README.md` | Sample | .NET |

### SSO (Single Sign-On)

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| SSO prehled a cross-reference | `sso/README.md` | Guide | MD |
| SSO s Microsoft Entra ID | `sso/entra-id/README.md` | Sample + HTML | HTML |
| SSO s Okta | `sso/okta/README.md` | Sample | - |

### Testovani

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Testovani - prehled | `testing/README.md` | Guide | MD |
| Funkcionalni testy s pytest | `testing/functional/README.md` | Guide | MD |
| Pytest + Agents SDK | `testing/functional/PytestAgentsSDK/README.md` | Sample | Python |
| Response analysis s Agents SDK | `testing/functional/ResponseAnalysisAgentsSDK/README.md` | Sample | Python |
| Zatezove testovani - prehled | `testing/load/README.md` | Guide | MD |
| JMeter multi-thread group test | `testing/load/JMeterMultiThreadGroup/README.md` | Sample | JMeter |

### Custom UI

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Custom UI - prehled | `ui/custom-ui/README.md` | Guide | MD |
| React chat UI (Assistant UI library) | `ui/custom-ui/assistant-ui/` | Sample | React |
| DirectLine JS chat (bez WebChat) | `ui/custom-ui/directline-js/README.md` | Sample | JavaScript |
| Zobrazeni reasoning a citaci agenta | `ui/custom-ui/reasoning-display/README.md` | Sample | - |
| WebChat React klient s auth | `ui/custom-ui/webchat-react/README.md` | Sample | Node/React |
| Web klient s auth | `ui/custom-ui/webclient/README.md` | Sample | Node |

### Embed do externich platforem

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Embed - prehled | `ui/embed/README.md` | Guide | MD |
| Minimalizovatelny chat widget (webova stranka) | `ui/embed/minimizable-widget/README.md` | Sample | JavaScript |
| ServiceNow floating widget | `ui/embed/servicenow-widget/README.md` | Sample | JavaScript |
| SharePoint app customizer + SSO | `ui/embed/sharepoint-customizer/README.md` | Sample | SPFx |
| D365 Customer Service + Okta SSO | `ui/embed/d365-cs-okta/README.md` | Sample | - |
| D365 Customer Service + SharePoint SSO | `ui/embed/d365-cs-sharepoint/README.md` | Sample | - |
| PCF control pro Power Apps canvas app | `ui/embed/pcf-canvas-app/README.md` | Sample | PCF |
| Typeahead suggestions pro WebChat | `ui/embed/typeahead-suggestions/README.md` | Sample | JavaScript |

### Contact Center Handoff

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Contact center - prehled | `contact-center/README.md` | Guide | MD |
| Skill-based handoff na live agenta | `contact-center/skill-handoff/README.md` | Sample | - |
| Contoso Live Chat App (ukazka) | `contact-center/skill-handoff/ContosoLiveChatApp/README.md` | Sample | - |
| Handover to Live Agent sample | `contact-center/skill-handoff/HandoverToLiveAgentSample/README.md` | Sample | - |
| Salesforce Einstein Bot integrace | `contact-center/salesforce/README.md` | Sample | - |
| ServiceNow Virtual Agent integrace | `contact-center/servicenow/README.md` | Sample | - |
| Genesys handoff (.NET) | `contact-center/genesys-handoff/README.md` | Sample | .NET |

### Authoring - Solutions a Snippets

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Authoring - prehled | `authoring/README.md` | Guide | MD |
| Importovatelne solutions (PnP format) | `authoring/solutions/README.md` | Guide | MD |
| Account + Contact lookup (multi-agent) | `authoring/solutions/account-contact-lookup/README.md` | Solution | Dataverse |
| Auto-detekce jazyka uzivatele | `authoring/solutions/auto-detect-language/README.md` | Solution | Dataverse |
| Dataverse indexer pro agent knowledge | `authoring/solutions/dataverse-indexer/README.md` | Solution | Dataverse |
| Feedback analyzer (MDA + workflows) | `authoring/solutions/feedback-analyzer/README.md` | Solution | Dataverse |
| Generativni chitchat komponenta | `authoring/solutions/generative-chitchat/README.md` | Solution | Dataverse |
| Resume/job finder (Dataverse matching) | `authoring/solutions/resume-job-finder/README.md` | Solution | Dataverse |
| Topic snippets - copy-paste | `authoring/snippets/README.md` | Snippets | YAML |
| Topic snippets katalog | `authoring/snippets/topics/README.md` | Snippets | YAML |

### Infrastruktura a Guides

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| VNet podpora - ARM template | `infrastructure/vnet-support/template.json` | ARM Template | JSON |
| VNet konfigurace - navod | `infrastructure/vnet-support/README.md` | Guide | MD |
| Implementation guide (PPTX) | `guides/implementation-guide/README.md` | Guide | PPTX |
| Workshop materialy (PPTX + lab files) | `guides/workshop/README.md` | Guide | PPTX/ZIP |
| Proctor instructions pro workshop | `guides/workshop/PROCTOR_INSTRUCTIONS.md` | Guide | MD |
| Migrace z Power Virtual Agents | `MIGRATION.md` | Guide | MD |

### Employee Self-Service Agent (deprecated)

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| ESS Agent prehled | `EmployeeSelfServiceAgent/README.md` | Sample | MD |
| Workday integrace | `EmployeeSelfServiceAgent/Workday/README.md` | Sample | MD |
| Facilities management | `EmployeeSelfServiceAgent/Facilities/README.md` | Sample | MD |
| ESS evaluacni vzorky | `EmployeeSelfServiceAgent/ESSEvaluationSamples/README.md` | Sample | MD |

## Key patterns

### MCP integrace s Copilot Studio
1. Vytvorit MCP server (TypeScript/Python) - viz `extensibility/mcp/search-species-resources-typescript/`
2. Definovat tools a resources v MCP serveru
3. Pripojit do Copilot Studio jako action
4. Predavat MCP resources jako vstupy - viz `extensibility/mcp/pass-resources-as-inputs/`

### A2A (Agent-to-Agent) komunikace
1. Implementovat A2A protokol - viz `extensibility/a2a/Simple-A2A-Sample/`
2. Umoznuje komunikaci mezi Copilot Studio agenty a dalsimi AI agenty

### Contact center handoff flow
1. Agent vede konverzaci s uzivatelem
2. Pri eskalaci preda kontext na live agenta
3. Platformy: Salesforce, ServiceNow, Genesys, nebo vlastni skill handoff

### Import PnP solution
1. Stahnout `.zip` z `authoring/solutions/{nazev}/solution/`
2. Importovat pres make.powerapps.com > Solutions > Import
3. Nakonfigurovat connection references a environment variables

### Testovaci strategie
- **Funkcionalni testy**: pytest + Agents SDK (`testing/functional/PytestAgentsSDK/`)
- **Response analysis**: automaticka analyza odpovedi (`testing/functional/ResponseAnalysisAgentsSDK/`)
- **Zatezove testy**: JMeter multi-thread (`testing/load/JMeterMultiThreadGroup/`)

## Prerequisites

- Microsoft Copilot Studio licence (trial nebo placena)
- Power Platform environment pro solutions
- Pro SSO: Entra ID app registration nebo Okta konfigurace
- Pro Agents SDK samples: .NET 6+, Node.js, nebo Python
- Pro MCP integrace: Node.js 18+ (TypeScript MCP server)
- Pro testovani: Python 3.9+ (pytest), Apache JMeter (load testy)
- Pro embed: pristup k cilove platforme (SharePoint, ServiceNow, D365, Power Apps)
