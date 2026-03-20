# INDEX: anthropic-skills

> SKILL.md open standard od Anthropic -- 17 referenčních skills pro Claude, specifikace formátu a template pro tvorbu vlastních skills.

## Use cases

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| **Specifikace formátu** | | | |
| Pochopit SKILL.md standard (YAML frontmatter + markdown instrukce) | `spec/agent-skills-spec.md` | spec | - |
| Použít template pro nový skill | `template/SKILL.md` | template | - |
| Vytvořit a optimalizovat skill (eval, benchmark, packaging) | `skills/skill-creator/SKILL.md` | skill | Python |
| **Kreativní & Design skills** | | | |
| Generovat algoritmické umění (p5.js, flow fields, particle systems) | `skills/algorithmic-art/SKILL.md` | skill | JavaScript |
| Vytvořit vizuální design (postery, art) jako .png/.pdf | `skills/canvas-design/SKILL.md` | skill | - |
| Vytvořit produkční frontend UI (React, Tailwind, shadcn/ui) | `skills/frontend-design/SKILL.md` | skill | TypeScript/CSS |
| Vytvořit komplexní HTML artifacts s React/shadcn/routing | `skills/web-artifacts-builder/SKILL.md` | skill | TypeScript |
| Aplikovat brand barvy a typografii Anthropic | `skills/brand-guidelines/SKILL.md` | skill | - |
| Stylovat artifacts pomocí 10 přednastavených témat | `skills/theme-factory/SKILL.md` | skill | - |
| Vytvořit animované GIFy optimalizované pro Slack | `skills/slack-gif-creator/SKILL.md` | skill | Python |
| **Development & Technical skills** | | | |
| Programovat s Claude API / Anthropic SDK / Agent SDK | `skills/claude-api/SKILL.md` | skill | Python/TS/Go/C#/Java/PHP |
| Buildovat MCP servery (Python FastMCP / Node MCP SDK) | `skills/mcp-builder/SKILL.md` | skill | Python/TypeScript |
| Testovat webové aplikace pomocí Playwright | `skills/webapp-testing/SKILL.md` | skill | Python |
| **Document skills (source-available)** | | | |
| Vytvářet a editovat Word dokumenty (.docx) | `skills/docx/SKILL.md` | skill | Python |
| Pracovat s PDF soubory (čtení, merge, split, OCR, formuláře) | `skills/pdf/SKILL.md` | skill | Python |
| Vytvářet PowerPoint prezentace (.pptx) | `skills/pptx/SKILL.md` | skill | Python |
| Pracovat s Excel soubory (.xlsx, .csv, tabulky, grafy) | `skills/xlsx/SKILL.md` | skill | Python |
| **Enterprise & Communication skills** | | | |
| Psát interní komunikaci (status reporty, newslettery, FAQ) | `skills/internal-comms/SKILL.md` | skill | - |
| Co-authoring dokumentace (specs, proposals, decision docs) | `skills/doc-coauthoring/SKILL.md` | skill | - |

## Klíčové patterny

- **Struktura skillu**: Složka s `SKILL.md` obsahujícím YAML frontmatter (`name`, `description`) + markdown instrukce
- **Trigger description**: Pole `description` v YAML určuje, kdy se skill aktivuje -- musí být co nejpřesnější
- **Doplňkové soubory**: Skill může obsahovat scripts, templates, examples a reference materiály
- **Evaluace**: `skills/skill-creator/` obsahuje nástroje pro eval (`scripts/run_eval.py`), benchmark (`scripts/aggregate_benchmark.py`) a packaging (`scripts/package_skill.py`)
- **Instalace v Claude Code**: `/plugin marketplace add anthropics/skills` a pak `/plugin install example-skills@anthropic-agent-skills`
- **Claude.ai**: Skills jsou dostupné na placených plánech, custom skills se nahrávají přes UI
- **API**: Skills se dají použít přes Claude API -- viz [Skills API Quickstart](https://docs.claude.com/en/api/skills-guide)

## Prerequisites

- Claude Code, Claude.ai (placený plán) nebo Claude API klíč
- Pro Python skills: Python 3.10+, relevantní závislosti (Playwright, Pillow, python-pptx apod.)
- Pro JS skills: Node.js 18+
- Pro document skills: specifické Python knihovny dle SKILL.md
