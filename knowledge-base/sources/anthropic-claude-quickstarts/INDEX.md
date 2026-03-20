# INDEX: anthropic-claude-quickstarts

> Kolekce quickstart projektů od Anthropic pro rychlý start s Claude API -- agenti, autonomní kódování, browser automation, computer use, customer support a finanční analýza.

## Use cases

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| **Agents framework** | | | |
| Vytvořit agenta s tool use (web search, code exec, file tools, MCP) | `agents/agent.py` | framework | Python |
| Připojit MCP tool k agentovi | `agents/tools/mcp_tool.py` | tool | Python |
| Implementovat web search tool | `agents/tools/web_search.py` | tool | Python |
| Implementovat code execution tool | `agents/tools/code_execution.py` | tool | Python |
| Implementovat file tools (read/write) | `agents/tools/file_tools.py` | tool | Python |
| Spravovat konverzační historii agenta | `agents/utils/history_util.py` | util | Python |
| Vyzkoušet agenta interaktivně (Jupyter notebook) | `agents/agent_demo.ipynb` | demo | Python |
| **Autonomní kódování** | | | |
| Spustit autonomního coding agenta (two-agent pattern) | `autonomous-coding/agent.py` | agent | Python |
| Pochopit initializer + coding agent orchestraci | `autonomous-coding/prompts/initializer_prompt.md` | prompt | Markdown |
| Pochopit coding prompt pro agenta | `autonomous-coding/prompts/coding_prompt.md` | prompt | Markdown |
| Definovat specifikaci aplikace pro agenta | `autonomous-coding/prompts/app_spec.txt` | config | Text |
| Implementovat sandbox security pro autonomní agenty | `autonomous-coding/security.py` | util | Python |
| **Browser automation (Browser Tools API)** | | | |
| Spustit browser automation demo (Streamlit UI + Playwright) | `browser-use-demo/browser_use_demo/streamlit.py` | app | Python |
| Implementovat browser tool (navigace, DOM, formuláře) | `browser-use-demo/browser_use_demo/tools/browser.py` | tool | Python |
| Implementovat agentic loop pro browser automation | `browser-use-demo/browser_use_demo/loop.py` | loop | Python |
| Spustit browser demo v Dockeru | `browser-use-demo/Dockerfile` | infra | Docker |
| **Computer Use** | | | |
| Spustit computer use demo (ovládání desktopu) | `computer-use-demo/computer_use_demo/streamlit.py` | app | Python |
| Implementovat computer tool (screenshot, click, type, scroll) | `computer-use-demo/computer_use_demo/tools/computer.py` | tool | Python |
| Implementovat bash tool pro computer use | `computer-use-demo/computer_use_demo/tools/bash.py` | tool | Python |
| Implementovat text editor tool | `computer-use-demo/computer_use_demo/tools/edit.py` | tool | Python |
| Implementovat agentic loop pro computer use | `computer-use-demo/computer_use_demo/loop.py` | loop | Python |
| Buildovat Docker image pro computer use | `computer-use-demo/Dockerfile` | infra | Docker |
| **Customer Support Agent** | | | |
| Spustit customer support agenta (Next.js + Claude API) | `customer-support-agent/app/api/chat/route.ts` | API | TypeScript |
| Procházet UI komponenty (chat, sidebar, navbar) | `customer-support-agent/components/ChatArea.tsx` | component | TypeScript |
| Konfigurace agenta a knowledge base kategorií | `customer-support-agent/config.ts` | config | TypeScript |
| **Financial Data Analyst** | | | |
| Spustit finanční analytika (Next.js + Claude API + vizualizace) | `financial-data-analyst/app/api/finance/route.ts` | API | TypeScript |
| Renderovat interaktivní grafy (Recharts) | `financial-data-analyst/components/ChartRenderer.tsx` | component | TypeScript |
| Zpracovat nahrané soubory pro analýzu | `financial-data-analyst/utils/fileHandling.ts` | util | TypeScript |

## Klíčové patterny

- **Agentic loop**: Všechny projekty implementují smyčku Claude API volání -> tool use -> zpracování výsledku -> další volání
- **Tool abstrakce**: `agents/tools/base.py` definuje `BaseTool` třídu -- nové tooly se registrují přes `ToolCollection`
- **MCP integrace**: `agents/tools/mcp_tool.py` ukazuje jak propojit agenta s MCP serverem
- **Two-agent pattern**: `autonomous-coding/` používá initializer agenta (plánuje) + coding agenta (implementuje)
- **Docker sandboxing**: Computer use i browser demo běží v Docker kontejnerech s VNC pro vizualizaci
- **Streamlit UI**: Computer use a browser demo používají Streamlit jako frontend
- **Next.js pattern**: Customer support a financial analyst používají Next.js App Router s API routes

## Prerequisites

- Anthropic API klíč (`ANTHROPIC_API_KEY`)
- **Agents / Autonomous coding**: Python 3.10+, `pip install anthropic`
- **Browser demo**: Docker, Playwright
- **Computer use demo**: Docker (VNC, xvfb, mutter pro desktop environment)
- **Customer support / Financial analyst**: Node.js 18+, npm
