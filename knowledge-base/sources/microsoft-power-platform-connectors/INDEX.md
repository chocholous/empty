# Power Platform Connectors - INDEX

> Open-source repozitar 1 100+ konektorovych definic pro Power Apps, Power Automate a Azure Logic Apps. Obsahuje certified, independent-publisher a custom connectory ve formatu OpenAPI 2.0 (Swagger).

## Struktura konektoru

Kazdy konektor je adresar s temito soubory:

| Soubor | Ucel |
|--------|------|
| `apiDefinition.swagger.json` | OpenAPI 2.0 definice - endpointy, parametry, responses |
| `apiProperties.json` | Metadata konektoru - auth, brand color, policy templates |
| `readme.md` / `Readme.md` | Popis konektoru, pouziti, priklady |

## Kategorie konektoru

| Kategorie | Cesta | Pocet | Popis |
|-----------|-------|-------|-------|
| Certified | `certified-connectors/` | 668 | Oficalni konektory od partneru, deployed out-of-box |
| Independent Publisher | `independent-publisher-connectors/` | 454 | Community konektory (MVP, developeri), premium |
| Custom | `custom-connectors/` | 23 | Ukazkove custom konektory vcetne MCP integrace |

## Use case tabulka

### Hledani a pouziti konektoru

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Najit certified konektor podle jmena | `certified-connectors/{nazev}/` | Swagger + config | JSON |
| Najit independent publisher konektor | `independent-publisher-connectors/{nazev}/` | Swagger + config | JSON |
| Najit custom konektor (sample) | `custom-connectors/{nazev}/` | Swagger + config | JSON |
| Precist API definici konektoru | `*/apiDefinition.swagger.json` | OpenAPI 2.0 | JSON |
| Zjistit auth metodu konektoru | `*/apiProperties.json` | Config | JSON |
| Zjistit dostupne operace/endpointy | `*/apiDefinition.swagger.json` → `paths` | Swagger | JSON |

### M365 / Azure konektory (certified)

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Microsoft 365 Lighthouse | `certified-connectors/Microsoft 365 Lighthouse/` | Swagger | JSON |
| Microsoft Bookings | `certified-connectors/Microsoft Bookings/` | Swagger | JSON |
| Microsoft Graph Security | `certified-connectors/MicrosoftGraphSecurity/` | Swagger | JSON |
| Office 365 Users | `certified-connectors/Office 365 Users/` | Swagger | JSON |
| Office 365 Groups Mail | `certified-connectors/Office365GroupsMail/` | Swagger | JSON |
| Outlook Tasks | `certified-connectors/OutlookTasks/` | Swagger | JSON |
| Azure AD | `certified-connectors/AzureAD/` | Swagger | JSON |
| Azure IoT Central | `certified-connectors/AzureIoTCentral/` | Swagger | JSON |
| Azure Digital Twins | `certified-connectors/AzureDigitalTwins/` | Swagger | JSON |
| Azure Communication Services Chat | `certified-connectors/Azure Communication Services Chat/` | Swagger | JSON |
| Azure Communication Services Email | `certified-connectors/Azure Communication Services Email/` | Swagger | JSON |
| Azure Communication Services SMS Events | `certified-connectors/Azure Communication Services SMS Events/` | Swagger | JSON |
| Azure Machine Learning | `certified-connectors/Azure Machine Learning/` | Swagger | JSON |
| Dynamics 365 Translation Service | `certified-connectors/Dynamics 365 Translation Service/` | Swagger | JSON |
| Dynamics 365 Fraud Protection | `certified-connectors/Dynamics365FraudProtection/` | Swagger | JSON |
| Teams-Spirit | `certified-connectors/Teams-Spirit/` | Swagger | JSON |
| School Data Sync v2 | `certified-connectors/microsoftschooldatasyncv2/` | Swagger | JSON |

### Independent Publisher - M365 a popularnich sluzby

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| MS Graph Groups and Users | `independent-publisher-connectors/MS Graph Groups and Users/` | Swagger | JSON |
| Microsoft Acronyms | `independent-publisher-connectors/Microsoft Acronyms/` | Swagger | JSON |
| Microsoft D365CE v9 OnPrem | `independent-publisher-connectors/Microsoft D365CE v9 OnPrem/` | Swagger | JSON |
| Microsoft Graph Add Users | `independent-publisher-connectors/Microsoft Graph Add Users/` | Swagger | JSON |
| Microsoft Learn Catalog | `independent-publisher-connectors/Microsoft Learn Catalog/` | Swagger | JSON |
| Microsoft Partner Center | `independent-publisher-connectors/Microsoft Partner Center/` | Swagger | JSON |
| Azure AD Applications | `independent-publisher-connectors/AzureADApplications/` | Swagger | JSON |

### Independent Publisher - popularnich externi sluzby

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| OpenAI | `independent-publisher-connectors/OpenAI/` | Swagger | JSON |
| OpenAI Assistants | `independent-publisher-connectors/OpenAI Assistants/` | Swagger | JSON |
| OpenAI GPT-4 | `independent-publisher-connectors/OpenAI GPT-4/` | Swagger | JSON |
| GitHub Gists | `independent-publisher-connectors/GitHub Gists/` | Swagger | JSON |
| GitHub Utils | `independent-publisher-connectors/GitHub Utils/` | Swagger | JSON |
| Discord | `independent-publisher-connectors/Discord/` | Swagger | JSON |
| Notion | `independent-publisher-connectors/Notion/` | Swagger | JSON |
| Atlassian Jira | `independent-publisher-connectors/Atlassian Jira/` | Swagger | JSON |
| Jira Search | `independent-publisher-connectors/JiraSearch/` | Swagger | JSON |
| Telegram Bot | `independent-publisher-connectors/Telegram Bot/` | Swagger | JSON |
| WhatsApp | `independent-publisher-connectors/WhatsApp/` | Swagger | JSON |

### Custom konektory - MCP integrace

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| MCP Server via SSE transport | `custom-connectors/MCP-SSE/` | Swagger + config | JSON |
| MCP Server via Streamable HTTP | `custom-connectors/MCP-Streamable-HTTP/` | Swagger + config | JSON |
| Azure OpenAI Service | `custom-connectors/AzureOpenAIService/` | Swagger + config | JSON |
| Azure Key Vault | `custom-connectors/AzureKeyVault/` | Swagger + config | JSON |
| Azure AD Phone Methods | `custom-connectors/AzureADPhoneMethods/` | Swagger + config | JSON |
| Azure AD IP | `custom-connectors/AzureAdIp/` | Swagger + config | JSON |
| Office 365 Groups | `custom-connectors/Office365Groups/` | Swagger + config | JSON |
| ServiceNow | `custom-connectors/ServiceNow/` | Swagger + config | JSON |
| Snowflake | `custom-connectors/Snowflake/` | Swagger + config | JSON |
| Facebook | `custom-connectors/Facebook/` | Swagger + config | JSON |
| Instagram Professional | `custom-connectors/Instagram Professional/` | Swagger + config | JSON |
| Copilot For Finance Communications | `custom-connectors/CopilotForFinanceCommunications/` | Swagger + config | JSON |

### Vyvoj a validace konektoru

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Template pro certified konektor | `templates/certified-connectors/` | Template | JSON |
| Template pro independent publisher | `templates/Independent Publisher/` | Template | JSON |
| JSON schema pro apiDefinition | `schemas/apiDefinition.swagger.schema.json` | JSON Schema | JSON |
| JSON schema pro apiProperties | `schemas/paconn-apiProperties.schema.json` | JSON Schema | JSON |
| JSON schema pro paconn settings | `schemas/paconn-settings.schema.json` | JSON Schema | JSON |
| Validator script (PowerShell) | `scripts/ConnectorPackageValidator.ps1` | Script | PowerShell |
| Paconn CLI tools | `tools/paconn-cli/` | CLI | Python |

## Key patterns

### Jak najit konektor
1. Urcit kategorii: `certified-connectors/`, `independent-publisher-connectors/`, `custom-connectors/`
2. Hledat adresar podle jmena sluzby
3. Otevrit `apiDefinition.swagger.json` pro dostupne operace
4. Zkontrolovat `apiProperties.json` pro auth typ (API key, OAuth2, atd.)

### Jak cist Swagger definici
- `info.title` - nazev konektoru
- `host` + `basePath` - API endpoint
- `paths` - dostupne operace (GET, POST, PUT, DELETE)
- `definitions` - datove modely
- `securityDefinitions` - auth schema

### Jak vytvorit novy konektor
1. Zkopirovat template z `templates/certified-connectors/` nebo `templates/Independent Publisher/`
2. Vyplnit `apiDefinition.swagger.json` s OpenAPI 2.0 definici
3. Nastavit `apiProperties.json` s auth a brand info
4. Pridat `readme.md` s popisem
5. Validovat pomoci `scripts/ConnectorPackageValidator.ps1`

### MCP-to-Power Platform bridge
- `custom-connectors/MCP-SSE/` - MCP server pripojeni pres Server-Sent Events
- `custom-connectors/MCP-Streamable-HTTP/` - MCP server pres Streamable HTTP transport
- Umoznuje propojit MCP tools s Power Automate a Power Apps

## Prerequisites

- Power Platform environment (Power Apps / Power Automate / Logic Apps)
- Pro vyvoj: `paconn` CLI (`tools/paconn-cli/`) nebo Power Platform CLI
- Pro validaci: PowerShell (`scripts/ConnectorPackageValidator.ps1`)
- Pro custom konektory: prislusne API klice nebo OAuth credentials
