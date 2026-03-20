# Semantic Kernel - Skills & Plugins

## Přehled

Semantic Kernel (SK) je Microsoft enterprise AI orchestration framework.
22k+ stars, Python + .NET + Java, model-agnostic.

## Definice skill (kernel function)

```python
from semantic_kernel.functions import kernel_function
from typing import Annotated

class MyPlugin:
    @kernel_function(name="search_docs", description="Search SharePoint documents")
    def search_docs(
        self,
        query: Annotated[str, "Search query"],
        site: Annotated[str, "SharePoint site URL"] = "default"
    ) -> Annotated[str, "Search results as JSON"]:
        # implementace
        return json.dumps(results)
```

### Typy funkcí
1. **Native Functions** - Python/C# metody s @kernel_function
2. **Prompt Functions** - YAML šablony s {{$variable}}
3. **OpenAPI Functions** - Auto-generované z OpenAPI specifikací

## M365 Plugins (.NET Plugins.MsGraph)

### EmailPlugin
- **Connector:** OutlookMailConnector
- **Operations:** SendEmail, GetEmails, SearchEmails
- **Model:** EmailMessage, EmailAddress

### CalendarPlugin
- **Connector:** OutlookCalendarConnector
- **Operations:** Create, update, query events
- **Model:** CalendarEvent

### CloudDrivePlugin
- OneDrive/SharePoint file operations

### TaskListPlugin
- Microsoft ToDo integration
- Create, update, organize tasks

### OrganizationHierarchyPlugin
- Azure AD / Entra ID org structure queries

### Autentizace
- MSAL-based (LocalUserMSALCredentialManager)
- Azure AD token-based
- Delegated + app permissions

## MCP Integrace v SK

SK má nativní MCP podporu (`semantic_kernel.connectors.mcp`):

```python
from semantic_kernel.connectors.mcp import MCPPluginBase

# Automaticky konvertuje MCP tools → SK functions
mcp_plugin = MCPPluginBase(
    transport="stdio",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/data"]
)
```

### Content bridging
- MCP TextContent ↔ SK TextContent
- MCP ImageContent ↔ SK ImageContent
- MCP ResourceLink ↔ SK BinaryContent
- MCP ToolUseContent ↔ SK FunctionCallContent

## Agent Framework

### Typy agentů
| Agent | Popis | Use Case |
|-------|-------|----------|
| ChatCompletionAgent | Základní LLM agent | General purpose |
| OpenAIAssistantAgent | OpenAI Assistants API | Code interpreter, file search |
| AzureAIAgent | Azure AI Agents | Enterprise Azure |
| BedrockAgent | AWS Bedrock | AWS environment |
| CopilotStudioAgent | Copilot Studio bridge | M365 integrace |

### Multi-agent orchestrace
```python
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.agents.group_chat import AgentGroupChat

billing = ChatCompletionAgent(name="Billing", instructions="Handle billing")
support = ChatCompletionAgent(name="Support", instructions="Handle support")

group = AgentGroupChat(agents=[billing, support])
result = await group.invoke("I need help with my invoice")
```

### Orchestrace patterns
- **Sequential** - krok za krokem
- **Concurrent** - paralelní agenti
- **Handoffs** - předávání mezi agenty
- **GroupChat** - strukturovaná konverzace

## Vector Stores / RAG

SK podporuje 15+ vector stores:
Azure AI Search, CosmosDB, Chroma, Pinecone, PostgreSQL/pgVector, Qdrant, Redis, Weaviate, Milvus, MongoDB Atlas, AstraDB, USearch

## Relevance pro tech stacky

| Stack | SK použití |
|-------|-----------|
| Copilot Studio | CopilotStudioAgent bridge |
| Terminal | Python SDK pro CLI agent workflows |
| Claude Code | MCP integrace, reference patterns |
| VS Code | Extension development s SK |
