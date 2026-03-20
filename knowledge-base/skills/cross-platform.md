# Cross-Platform Skills & Patterns

## SKILL.md - Otevřený Standard (Key Takeaway)

**SKILL.md je otevřený standard** vytvořený Anthropic (late 2025), přijatý napříč platformami:

| Platforma | Podpora | Od kdy |
|-----------|---------|--------|
| **Claude Code** | Creator | 2025 |
| **GitHub Copilot** | CLI + VS Code | Dec 2025 |
| **OpenAI Codex CLI** | Adopted | Dec 2025 |
| **Cursor IDE** | Adopted | Jan 2026 (v2.4) |
| **Semantic Kernel** | Python SDK | 2026 |
| **Copilot Studio** | Bridge via plugin | 2026 |

Jeden skill napsaný jednou funguje ve všech SKILL.md-kompatibilních agentech.

### SKILL.md formát
```yaml
---
name: my-skill-name           # lowercase, hyphens only (required)
description: Does X when Y    # third person (required)
allowed-tools: Bash(gh *), Read, Grep  # optional - omezení nástrojů
context: fork                  # optional - izolovaný subagent
disable-model-invocation: true # optional - jen user může zavolat
user-invocable: false          # optional - jen AI může zavolat
---
# Skill Instructions (Markdown)

## What this skill does
[Popis pro AI agenta]

## Steps
1. Do X
2. Do Y
3. Return Z
```

### Adresářová struktura
```
my-skill/
├── SKILL.md          # Povinný - definice skill
├── scripts/          # Volitelný - spustitelné skripty
├── references/       # Volitelný - docs načtené do kontextu
└── assets/           # Volitelný - šablony, binárky
```

### Progressive Disclosure
Všechny platformy používají 3-úrovňový loading:
1. **Discovery** (~100 tokenů) - jméno + popis, injektováno do system promptu
2. **Instructions** (<5k tokenů) - plný obsah SKILL.md při aktivaci
3. **Resources** - reference soubory, skripty, na vyžádání

Budget: 2% context window (default 16,000 chars, konfigurovatelné přes `SLASH_COMMAND_TOOL_CHAR_BUDGET`).

## Skills definice podle platformy

### Claude Code
- **Formát:** SKILL.md (open standard creator)
- **Personal:** `~/.claude/skills/`
- **Project:** `.claude/skills/`
- **Built-in skills:** `/simplify`, `/review`, `/batch`, `/loop`, `/debug`, `/claude-api`
- **Slash commands** merged do skills systému od v2.1.3
- **Zdroje:** [anthropics/skills](https://github.com/anthropics/skills), [skillsmp.com](https://skillsmp.com) (500k+ skills)

### GitHub Copilot
- **Formát:** SKILL.md (adopted standard)
- **Project:** `.github/skills/` (čte i `.claude/skills/`)
- **Personal:** `~/.copilot/skills/`
- **Built-in:** `@workspace`, `@terminal`, `@vscode`, `/fix`, `/tests`, `/new`, `/explain`
- **VS Code:** Agent Skills od v1.108 (`chat.useAgentSkills`)
- **Agent Plugins (preview):** Bundles s skills + agents + hooks + MCP
- **Zdroje:** [github/awesome-copilot](https://github.com/github/awesome-copilot)

### OpenAI Codex CLI
- **Formát:** SKILL.md (adopted standard)
- **Personal:** `~/.codex/skills/`
- **Project:** `.codex/skills/`
- **Config:** `agents/openai.yaml` pro UI metadata, invocation policy
- **Install:** `$skill-installer` pro kurátované skills
- **GPT Actions:** OpenAPI schema pro REST API (ChatGPT Custom GPTs)

### Cursor IDE
- **3-vrstvý systém:**
  - **Rules** (.mdc) - Shape behavior, vždy/auto/on-demand/manual
  - **Skills** (SKILL.md od v2.4) - Domain-specific capabilities
  - **Commands** (.cursor/commands/*.md) - Saved prompt shortcuts
- **Filozofie:** "Rules guide. Skills do. Commands trigger."
- **Zdroje:** [dotcursorrules.com](https://dotcursorrules.com), [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules)

### Copilot Studio
- **Formát:** YAML (.mcs.yaml) - proprietární
- **Struktura:**
  ```
  agent-folder/
  ├── agent.mcs.yaml        # Hlavní definice
  ├── settings.mcs.yml      # Konfigurace
  ├── topics/               # Konverzační topics
  ├── actions/              # Connector akce
  ├── workflows/            # Agent tools
  ├── trigger/              # Event triggers
  └── knowledge/files/      # Knowledge sources
  ```
- **Vizuální authoring** + VS Code extension
- **Generative actions** - AI dynamicky vybírá plugins
- **Component Collections (GA)** - reusable balíčky across agents
- **Bridge:** [skills-for-copilot-studio](https://github.com/microsoft/skills-for-copilot-studio) - SKILL.md plugin pro authoring z terminálu (20x faster)

### Semantic Kernel
- **Formát:** @kernel_function dekorátor (Python/C#) + OpenAPI + MCP
- **Terminologie:** "Skills" přejmenováno na "Plugins"
- **3 způsoby importu:** Native code, OpenAPI spec, MCP Server
- **Best practice:** snake_case pro function names (LLM training bias)
- **SKILL.md support:** Python SDK podporuje open standard

## Srovnávací matice

| Feature | Claude Code | Copilot | Codex CLI | Cursor | Copilot Studio | SK |
|---------|-------------|---------|-----------|--------|----------------|-----|
| **SKILL.md** | Creator | Adopted | Adopted | Adopted | Bridge | Partial |
| **Personal store** | ~/.claude/ | ~/.copilot/ | ~/.codex/ | ~/.cursor/ | N/A | N/A |
| **Project store** | .claude/skills/ | .github/skills/ | .codex/skills/ | .cursor/ | agent-folder/ | code |
| **Visual authoring** | Ne | Ne | Ne | Ne | Ano (canvas) | Ne |
| **Script bundling** | Ano | Ano | Ano | Ano | Ano (workflows) | Ano |
| **M365 skills** | MCP servers | Extensions + MCP | GPT Actions | Rules + MCP | 1,400+ connectors | Plugins |
| **Slash commands** | Merged w/ skills | Built-in | Built-in | Separate | N/A | N/A |
| **Cross-platform** | CLI, SDK, web | CLI, VS Code, GH | CLI, IDE, web | IDE only | Web, VS Code, Teams | .NET, Py, Java |

## Instalace skills napříč platformami

### Jeden skill, všechny platformy
```bash
# Vytvořit skill
mkdir -p my-skill && cat > my-skill/SKILL.md << 'EOF'
---
name: azure-resource-checker
description: Checks Azure resource health and costs for the current subscription
allowed-tools: Bash
---
# Azure Resource Health Check

1. Run `az resource list -g $RESOURCE_GROUP --output table`
2. Check health: `az monitor metrics list --resource $ID`
3. Check costs: `az consumption usage list --top 10`
4. Summarize findings with recommendations
EOF

# Deploy do Claude Code
cp -r my-skill ~/.claude/skills/

# Deploy do GitHub Copilot
cp -r my-skill .github/skills/

# Deploy do Codex CLI
cp -r my-skill ~/.codex/skills/

# V Cursoru - skill se načte z .claude/skills/ automaticky
```

## Best Practices

### 1. Používejte progressive disclosure
Nedávejte vše do SKILL.md - použijte `references/` pro velké docs.

### 2. Popisujte CO, ne JAK
```yaml
# Dobře:
description: Finds and analyzes Azure cost anomalies across resource groups
# Špatně:
description: Runs az consumption usage list and parses JSON output
```

### 3. Jeden skill = jedna odpovědnost
Malé, fokusované skills > velké monolity.

### 4. Testujte s reálným LLM
Skills jsou interpretované modelem - behavior se může lišit.

### 5. Security
- `disable-model-invocation: true` pro destruktivní operace (deploy, delete)
- `allowed-tools` pro omezení nástrojů
- `context: fork` pro izolaci

### 6. Naming
- Gerund form: `generating-tests`, `checking-azure-health`
- Lowercase + hyphens only
- Third person descriptions

## Klíčové zdroje skills

| Zdroj | URL | Skills |
|-------|-----|--------|
| Skills Marketplace | [skillsmp.com](https://skillsmp.com) | 500k+ |
| Antigravity Awesome Skills | [github](https://github.com/sickn33/antigravity-awesome-skills) | 1,273+ |
| Awesome Claude Skills | [github](https://github.com/travisvn/awesome-claude-skills) | Community |
| Awesome Copilot | [github](https://github.com/github/awesome-copilot) | 208+ |
| Microsoft Skills | [github](https://github.com/microsoft/skills) | Official |
| MicrosoftDocs Agent Skills | [github](https://github.com/MicrosoftDocs/Agent-Skills) | Azure-focused |
| .NET Skills | [github](https://github.com/dotnet/skills) | .NET-focused |
| Anthropic Skills | [github](https://github.com/anthropics/skills) | Official |
| OpenAI Skills | [github](https://github.com/openai/skills) | Official |
| Skills for Copilot Studio | [github](https://github.com/microsoft/skills-for-copilot-studio) | Bridge |
