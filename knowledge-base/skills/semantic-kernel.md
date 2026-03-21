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

## Process Framework (orchestrace agentů)

```python
from semantic_kernel.processes import ProcessBuilder

# Define process steps
process = ProcessBuilder(name="CustomerSupport")
triage = process.add_step(TriageStep)
sentiment = process.add_step(SentimentStep)
resolution = process.add_step(ResolutionStep)

# Define flow
process.on_input_event("start").send_event_to(triage)
triage.on_event("billing").send_event_to(resolution, function_name="handle_billing")
triage.on_event("technical").send_event_to(sentiment)
sentiment.on_event("done").send_event_to(resolution, function_name="handle_technical")
```

## Copilot Agent Plugins (Graph API)

```csharp
// Import Graph API jako SK plugin z OpenAPI spec
await kernel.ImportPluginFromCopilotAgentPluginAsync(
    "graph-mail",
    new Uri("https://graph.microsoft.com/.well-known/openapi")
);

// Retrieval API (Build 2025) - query přímo do Microsoft semantic index
// Eliminuje potřebu vlastních vector stores
```

## Agent Factory Pattern (z Azure samples)

```python
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent, AzureAIAgent

class AgentBase:
    """Base class s singleton pattern"""

    async def initialize(self, kernel, configuration, project_client=None):
        if isinstance(configuration, ChatCompletionAgentConfig):
            self._agent = ChatCompletionAgent(
                kernel=kernel,
                name=configuration.name,
                instructions=configuration.instructions
            )
        elif isinstance(configuration, AzureAIAgentConfig):
            self._agent = AzureAIAgent(
                project_client=project_client,
                name=configuration.name,
                instructions=configuration.instructions,
                response_format=ResponseFormatJsonSchema(...)
            )
```

## Memory Integration

```python
# Store
await agent.store_memory_in_collection(
    collection_name="customer_profiles",
    content=profile_data,
    content_id=customer_id
)

# Retrieve
results = await agent.search_memory_in_collection(
    collection_name="customer_profiles",
    query="vip customers",
    max_result_count=10,
    min_relevance_score=0.75
)
```

## Relevance pro tech stacky

| Stack | SK použití |
|-------|-----------|
| Copilot Studio | CopilotStudioAgent bridge |
| Terminal | Python SDK pro CLI agent workflows |
| Claude Code | MCP integrace, reference patterns |
| VS Code | Extension development s SK |
