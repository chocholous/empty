# OpenAI Function Calling & GPT Actions

## Function Calling (Tool Use)

### Základní pattern
```python
import openai

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["location"]
        }
    }
}]

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather in Prague?"}],
    tools=tools,
    tool_choice="auto"  # auto | required | none | {"type":"function","function":{"name":"..."}}
)

# Execution loop
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        result = execute_function(tool_call.function.name, tool_call.function.arguments)
        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})
    # Send results back to model
    final = client.chat.completions.create(model="gpt-4", messages=messages, tools=tools)
```

### Best Practices
- Jasné, distinktivní popisy funkcí
- Deskriptivní jména parametrů
- Explicitní "required" pole
- Filtrujte tools na essentials (méně tokenů)
- Pro complex routing zvažte fine-tuning

## GPT Actions (ChatGPT Plugins)

GPT Actions jsou OpenAPI-based integrace pro Custom GPTs.

### Dostupné akce pro M365/Azure
| Akce | Popis | Zdroj |
|------|-------|-------|
| SharePoint Text | Čtení SharePoint dokumentů | openai-cookbook |
| SharePoint Docs | Upload/download dokumentů | openai-cookbook |
| Azure Functions middleware | Proxy pro libovolné Azure API | openai-cookbook |
| Azure AI Search + RAG | Vektorové vyhledávání | openai-cookbook |
| SQL Database | Přímé SQL queries | openai-cookbook |

### Azure Functions jako middleware
```python
# Pro GPT Actions které potřebují autentizaci nebo custom logiku
import azure.functions as func
from msgraph import GraphServiceClient

@app.route(route="sharepoint-search")
async def sharepoint_search(req: func.HttpRequest):
    query = req.params.get('query')
    client = GraphServiceClient(credential)
    results = await client.search.query(query)
    return func.HttpResponse(json.dumps(results))
```

## OpenAI Agents SDK

### Orchestrace pattern
```python
from openai.agents import Agent, Runner

triage = Agent(
    name="Triage",
    instructions="Route to appropriate specialist",
    tools=[transfer_to_billing, transfer_to_support]
)

billing = Agent(
    name="Billing",
    instructions="Handle billing questions",
    tools=[check_balance, process_refund]
)

# Handoff: Agent A → Agent B s plným kontextem
runner = Runner(agent=triage)
result = await runner.run("I need a refund")
```

### Multi-agent patterns
- **Triage → Specialist** routing
- **Parallel agents** pro nezávislé úkoly
- **Session memory** pro kontext across turns
- **Voice agents** pro hlasové interakce

## Responses API + MCP

OpenAI podporuje MCP přímo v Responses API:
```python
response = client.responses.create(
    model="gpt-4",
    input="Search our docs for deployment guide",
    tools=[{
        "type": "mcp",
        "server_label": "docs",
        "server_url": "https://docs-mcp.example.com/sse",
        "allowed_tools": ["search", "read_doc"]  # Filtrujte!
    }],
    # Cachování tool listů
    previous_response_id="resp_abc123"
)
```

### Best practices pro MCP + Responses API
- Filtrujte allowed_tools pro redukci kontextu
- Cachujte tool listy přes previous_response_id
- Kombinujte MCP s hosted tools (code_interpreter, web_search)
- Reasoning modely rezervujte pro complex tasks

## Structured Outputs

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "analysis",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
                    "confidence": {"type": "number"},
                    "summary": {"type": "string"}
                },
                "required": ["sentiment", "confidence", "summary"]
            }
        }
    }
)
```

## Multi-Agent s OpenAI Agents SDK

### Routine-based pattern (Swarm)
```python
from openai.agents import Agent, Runner

# Routines = system prompt + tools + conditional logic
triage = Agent(
    name="Triage",
    instructions="""Route customer requests:
    - Billing → transfer_to_billing
    - Technical → transfer_to_support
    - Sales → transfer_to_sales""",
    tools=[transfer_to_billing, transfer_to_support, transfer_to_sales]
)

billing = Agent(
    name="Billing",
    instructions="Handle billing. Tools: check_balance, process_refund",
    tools=[check_balance, process_refund]
)

# Handoff: triage → billing with full context
runner = Runner(agent=triage)
result = await runner.run("I need a refund for last month")
```

### Multi-Agent Best Practices
- **Specializace** - Jeden agent = jeden doménový kontext
- **Tool grouping** - Každý agent má jen relevantní tools (snižuje chybovost)
- **Triage pattern** - Hlavní agent routuje, neřeší
- **Handoffs** - Plný kontext se předává (ne jen summary)

## Responses API + MCP (nativní podpora)
```python
response = client.responses.create(
    model="gpt-4o",
    input="Search docs for deployment guide",
    tools=[{
        "type": "mcp",
        "server_label": "docs",
        "server_url": "https://docs-mcp.example.com/sse",
        "allowed_tools": ["search", "read_doc"]
    }],
    previous_response_id="resp_abc123"  # Cache tool lists
)
```
