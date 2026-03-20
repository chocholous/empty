#!/bin/bash
# Update source repositories for knowledge base
# Usage: ./update-sources.sh [--clone-dir /tmp/source-repos]

set -euo pipefail

CLONE_DIR="${1:-/tmp/ai-kb-sources}"

echo "=== AI Knowledge Base Source Updater ==="
echo "Clone directory: $CLONE_DIR"
echo ""

mkdir -p "$CLONE_DIR"

# Official repos to clone/update
declare -A REPOS=(
    ["mcp-servers"]="https://github.com/modelcontextprotocol/servers.git"
    ["mcp-typescript-sdk"]="https://github.com/modelcontextprotocol/typescript-sdk.git"
    ["mcp-spec"]="https://github.com/modelcontextprotocol/modelcontextprotocol.git"
    ["semantic-kernel"]="https://github.com/microsoft/semantic-kernel.git"
    ["openai-cookbook"]="https://github.com/openai/openai-cookbook.git"
    ["anthropic-cookbook"]="https://github.com/anthropics/anthropic-cookbook.git"
    ["microsoft-mcp"]="https://github.com/microsoft/mcp.git"
    ["microsoft-skills"]="https://github.com/microsoft/skills.git"
    ["agent-skills"]="https://github.com/MicrosoftDocs/Agent-Skills.git"
    ["awesome-copilot"]="https://github.com/github/awesome-copilot.git"
    ["copilot-extensions"]="https://github.com/copilot-extensions/preview-sdk.js.git"
    ["dotnet-skills"]="https://github.com/dotnet/skills.git"
    ["awesome-skills"]="https://github.com/sickn33/antigravity-awesome-skills.git"
    ["ms-docs-mcp"]="https://github.com/MicrosoftDocs/mcp.git"
    ["azure-devops-mcp"]="https://github.com/microsoft/azure-devops-mcp.git"
    ["copilot-for-azure"]="https://github.com/microsoft/GitHub-Copilot-for-Azure.git"
)

for name in "${!REPOS[@]}"; do
    url="${REPOS[$name]}"
    dir="$CLONE_DIR/$name"

    if [ -d "$dir/.git" ]; then
        echo "Updating $name..."
        (cd "$dir" && git pull --ff-only 2>/dev/null) || echo "  Warning: pull failed for $name"
    else
        echo "Cloning $name..."
        git clone --depth 1 "$url" "$dir" 2>/dev/null || echo "  Warning: clone failed for $name"
    fi
done

echo ""
echo "=== Done ==="
echo "Sources cloned to: $CLONE_DIR"
echo ""
echo "To explore:"
echo "  ls $CLONE_DIR/"
echo "  find $CLONE_DIR -name 'README.md' -maxdepth 2"
