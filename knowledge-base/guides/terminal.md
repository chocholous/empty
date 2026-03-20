# Terminal-Only Workflows - Kompletní průvodce

## Přehled

Terminálové AI workflows bez IDE. Pro servery, CI/CD, scripting, SSH sessions.

## Dostupné nástroje

### Claude Code (Anthropic)
```bash
# Interaktivní mode
claude

# One-shot command
claude -p "Explain this error: $(cat error.log)"

# Pipe input
cat code.py | claude -p "Review this code"

# S MCP
claude --mcp-config ~/.claude/mcp.json
```

### OpenAI Codex CLI
```bash
# Instalace
npm install -g @openai/codex

# Použití
codex "Create a Bicep template for Azure Container App"
```

## Skills pro terminal

### Claude Code skills v terminálu
```bash
# Skills fungují i v pure terminal mode
# .claude/skills/ se automaticky načtou

# Příklad: Azure operations skill
mkdir -p .claude/skills/azure/
cat > .claude/skills/azure/SKILL.md << 'EOF'
---
name: azure-ops
description: Azure resource management via CLI
tools: Bash
---
# Azure Operations
- `az group list --output table`
- `az resource list -g {rg} --output table`
- `az monitor metrics list --resource {id} --metric "CpuPercentage"`
EOF
```

### Semantic Kernel v Pythonu
```python
#!/usr/bin/env python3
"""Terminal-based AI agent with SK"""
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

async def main():
    kernel = Kernel()
    kernel.add_service(AzureChatCompletion(
        deployment_name="gpt-4",
        endpoint="https://myendpoint.openai.azure.com/",
        api_key=os.getenv("AZURE_OPENAI_KEY")
    ))

    agent = ChatCompletionAgent(
        kernel=kernel,
        name="Terminal Assistant",
        instructions="You help with Azure operations via CLI"
    )

    while True:
        user_input = input("You: ")
        if user_input == "exit": break
        response = await agent.get_response(messages=user_input)
        print(f"AI: {response}")

asyncio.run(main())
```

## MCP v terminálu

### Stdio transport (default pro terminal)
```bash
# MCP server běží jako subprocess
# Claude Code to řeší automaticky

# Manuální spuštění MCP serveru pro testování
npx @modelcontextprotocol/server-memory &
# Server komunikuje přes stdin/stdout JSON-RPC
```

### MCP konfigurace pro terminal
```json
// ~/.claude/mcp.json nebo .claude/settings.json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": { "MEMORY_FILE_PATH": "~/.ai-memory.jsonl" }
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git"]
    }
  }
}
```

## Scripting patterns

### CI/CD s AI
```bash
#!/bin/bash
# AI-assisted PR review v CI pipeline
claude -p "Review this diff for security issues:
$(git diff main...HEAD)" --output-format json > review.json

# Parse výsledky
jq '.issues[] | select(.severity == "HIGH")' review.json
```

### Batch processing
```bash
#!/bin/bash
# Analyzovat všechny Python soubory
for f in src/**/*.py; do
    echo "=== $f ==="
    claude -p "Find potential bugs in: $(cat $f)" 2>/dev/null
done
```

### Azure automation
```bash
#!/bin/bash
# AI-assisted Azure troubleshooting
RESOURCE_GROUP="rg-prod-weu-01"

# Získat metriky
METRICS=$(az monitor metrics list --resource-group $RESOURCE_GROUP --output json)

# AI analýza
claude -p "Analyze these Azure metrics and suggest optimizations: $METRICS"
```

## Best Practices

1. **Pipe-friendly** - Používejte `claude -p` pro scripting
2. **JSON output** - `--output-format json` pro parsování
3. **MCP memory** - Pro persistent kontext across sessions
4. **Skills** - `.claude/skills/` fungují i v terminal mode
5. **Env vars** - Credentials vždy přes environment variables
6. **Batch** - Paralelizujte s xargs/GNU parallel

## Srovnání terminálových AI nástrojů

| Feature | Claude Code | Codex CLI | az + AI |
|---------|-------------|-----------|---------|
| MCP support | Ano | Ne | Ne |
| Skills/plugins | .claude/skills/ | Ne | Ne |
| Pipe support | Ano | Ano | Ano |
| M365 integrace | Přes MCP | Ne | Azure nativní |
| Offline | Ne | Ne | Ne |
| Multi-file edit | Ano | Ano | Ne |
| Interactive | Ano | Ano | Ne |

## Zdroje

- [anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook)
- [microsoft/skills](https://github.com/microsoft/skills)
- [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
