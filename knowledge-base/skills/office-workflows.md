# Office Workflows — Kancelářské a business úkoly

## Přehled

Task-oriented průvodce pro běžné kancelářské a business úkoly. Každý workflow odkazuje na konkrétní skills, plugins a cookbooks z 15 zdrojových repozitářů.

**Klíčový princip:** Agent by měl najít relevantní skill/plugin/cookbook a podle něj realizovat úkol — ne všechno řešit od nuly.

**Dostupné pluginy:**
- [anthropics/anthropic-knowledge-work-plugins](https://github.com/anthropics/anthropic-knowledge-work-plugins) — 11 domain pluginů (sales, legal, finance, PM, data, support, engineering, design, marketing, HR, operations)
- [anthropics/anthropic-financial-services-plugins](https://github.com/anthropics/anthropic-financial-services-plugins) — 56 financial skills
- [anthropics/skills](https://github.com/anthropics/skills) — 17 reference skills (SKILL.md standard)

---

## Sales — Prodej a obchod

**Plugin:** `anthropic-knowledge-work-plugins/sales/`

### Call Prep (příprava na schůzku)

**Trigger:** "příprava na call", "call prep", "meeting prep", "co vědět o klientovi"

**Workflow:**
1. Získat kontext z nástrojů (CRM, email, chat, kalendář)
2. Web research na firmu a účastníky
3. Syntetizovat a generovat briefing

**Output:** Account snapshot, pozadí účastníků, historie, navrhovaný program, discovery otázky, potenciální námitky.

**Variace:** discovery call, demo, vyjednávání, check-in.

### Draft Outreach (prospecting email)

**Trigger:** "napiš email", "outreach", "prospecting", "oslovení klienta"

**Workflow:**
1. Research prospect (firma, role, novinky)
2. Najít hook: trigger event → mutual connection → their content → company initiative → role pain point
3. Napsat podle AIDA (Attention, Interest, Desire, Action)

**Typy:** cold outreach, warm outreach, re-engagement, post-event follow-up, LinkedIn message.

### Pipeline Review

**Trigger:** "pipeline review", "stav dealů", "forecast", "pipeline health"

**Health score:** stage progression (30%), activity recency (25%), close date accuracy (20%), contact coverage (15%), risk flags (10%).

**Risk flags:** stale 14+ dní, stuck 30+ dní, past close date, single-threaded.

### Account Research

**Trigger:** "research firmu", "account research", "zjisti o firmě"

**Output:** Quick take, company profile, key people, tech stack, prior relationship, qualification signals, doporučený přístup.

### Forecast

**Trigger:** "forecast", "predikce tržeb", "sales forecast"

**Default stage probabilities:** Closed Won 100%, Negotiation 80%, Proposal 60%, Evaluation 40%, Discovery 20%, Prospecting 10%.

**MCP konektory:** CRM (HubSpot, Close), Transcripts (Fireflies, Gong), Enrichment (Clay, ZoomInfo, Apollo), Chat (Slack, Teams), Email, Calendar.

---

## Legal — Právo a compliance

**Plugin:** `anthropic-knowledge-work-plugins/legal/`

### Contract Review (revize smlouvy)

**Trigger:** "zkontroluj smlouvu", "contract review", "revize kontraktu", "redline"

**Workflow:**
1. Analýza clause-by-clause proti playbooku (nebo generické standardy)
2. Tří-úrovňové hodnocení: GREEN (OK), YELLOW (vyjednat), RED (eskalovat)
3. Generování redlines s konkrétním jazykem a fallback pozicemi

**Kontrolované klauzule:**
- Limitation of Liability: cap, carveouts, mutual vs. unilateral
- Indemnification: rozsah, cap, IP infringement, data breach
- IP Ownership: pre-existing, developed, work-for-hire
- Data Protection: DPA, sub-processors, breach notification, cross-border
- Confidentiality: rozsah, trvání, výjimky
- Term & Termination: trvání, renewal, termination for convenience/cause

**Vyjednávací strategie:** Tier 1 must-haves, Tier 2 should-haves, Tier 3 nice-to-haves.

### NDA Triage

**Trigger:** "NDA", "triage NDA", "zhodnoť NDA"

**Klasifikace:** GREEN (standard, same-day), YELLOW (counsel review, 1-2 dny), RED (full legal, 3-5 dní).

**Screening:** 10 oblastí (mutual vs. unilateral, definice, povinnosti, výjimky, permitted disclosure, term, return/destruction, remedies, problematic provisions, governing law).

### Compliance Check

**Trigger:** "compliance", "GDPR", "ochrana dat", "privacy"

**Regulace:** GDPR, CCPA/CPRA, LGPD, POPIA, PIPEDA, PDPA, Australian Privacy Act, PIPL, UK GDPR.

**DPA checklist:** Subject matter, processor obligations, international transfers (SCC, TIA), data subject request handling.

**Příkazy:** `/review-contract`, `/triage-nda`, `/vendor-check [vendor]`, `/brief daily|topic|incident`, `/respond [inquiry-type]`

**Customizace:** Vytvořit `legal.local.md` s playbook organizace (standard positions, acceptable ranges, escalation triggers).

---

## Product Management

**Plugin:** `anthropic-knowledge-work-plugins/product-management/`

### Write Spec (PRD)

**Trigger:** "napiš spec", "PRD", "product spec", "feature spec", "specifikace"

**PRD struktura:**
1. Problem Statement (2-3 věty, evidence-grounded)
2. Goals (3-5 měřitelných výstupů)
3. Non-Goals (3-5 věcí mimo scope)
4. User Stories (As [user], I want [capability] so that [benefit])
5. Requirements (MoSCoW: P0 Must-Have, P1 Nice-to-Have, P2 Future)
6. Success Metrics (leading + lagging indicators)
7. Open Questions (kdo by měl odpovědět, blocking vs. non-blocking)

### Roadmap Update

**Trigger:** "roadmap", "prioritizace", "co dělat dál"

**Frameworks:** Now/Next/Later, Quarterly Themes, OKR-Aligned, Timeline/Gantt.

**Prioritizace:** RICE Score = (Reach × Impact × Confidence) / Effort.

**Capacity planning:** 70% planned, 20% tech health, 10% unplanned.

### Research Synthesis

**Trigger:** "syntetizuj research", "výzkum", "interview analýza"

**Metoda:** Familiarizace → Initial coding → Theme development → Review → Refinement → Report.

**Příkazy:** `/write-spec`, `/roadmap-update`, `/metrics-review`, `/competitive-brief`, `/brainstorm`

**Konektory:** Slack, Linear/Asana/Monday/Jira, Notion, Figma, Amplitude/Pendo, Intercom, Fireflies.

---

## Data Analysis — Analýza dat

**Plugin:** `anthropic-knowledge-work-plugins/data/`

### Write Query (natural language → SQL)

**Trigger:** "SQL dotaz", "napiš query", "data z databáze"

**Dialekty:** PostgreSQL, Snowflake, BigQuery, Redshift, Databricks, MySQL, SQL Server, DuckDB, SQLite.

**Best practices:**
- CTEs pro čitelnost (jedna CTE = jedna transformace)
- Nikdy `SELECT *`, filtrovat brzy
- `EXISTS` místo `IN` pro subquery
- Komentáře vysvětlující "proč"

### Analyze (datová analýza)

**Trigger:** "analyzuj data", "co říkají čísla", "trend", "proč metrika klesá"

**Úrovně:** Quick answer (jedna metrika), Full analysis (multi-dimenzionální), Formal report (kompletní).

**Validace:** Row count sanity, null checks, magnitude, trend continuity, aggregation logic.

### Vizualizace a dashboardy

**Příkazy:** `/create-viz`, `/build-dashboard`, `/explore-data`, `/validate`, `/statistical-analysis`

**Konektory:** Snowflake, Databricks, BigQuery, Definite, Hex, Amplitude, Jira.

---

## Customer Support

**Plugin:** `anthropic-knowledge-work-plugins/customer-support/`

### Ticket Triage

**Trigger:** "roztřiď ticket", "triage", "prioritizace ticketů"

**Kategorie:** Bug, How-to, Feature request, Billing, Account, Integration, Security, Data, Performance.

**Priority:**
- **P1 Critical** (1h SLA): production down, data loss, security breach
- **P2 High** (4h): major feature broken, no workaround
- **P3 Medium** (1 BD): partially broken with workaround
- **P4 Low** (2 BD): minor, cosmetic, feature request

**Routing:** Tier 1 (how-to, known), Tier 2 (bugs, complex), Engineering (confirmed bugs), Product (feature requests).

### Draft Response

**Trigger:** "napiš odpověď zákazníkovi", "draft response", "customer email"

**Struktura:** Acknowledgment (1-2 věty) → Core Message (1-3 odstavce) → Next Steps (1-3 bullets) → Closing.

**Délka:** Chat 1-4 věty, ticket 1-3 odstavce, email 3-5 max, escalation neomezená, executive 2-3.

**Příkazy:** `/escalate`, `/research`, `/kb-article`

**Konektory:** Slack, Intercom, HubSpot, Guru, Notion, Jira, M365.

---

## Enterprise Search

**Plugin:** `anthropic-knowledge-work-plugins/enterprise-search/`

### Search (hledání napříč zdroji)

**Trigger:** "najdi", "vyhledej", "kde je", "kdo ví o"

**Workflow:**
1. Zkontrolovat dostupné zdroje
2. Parsovat dotaz (intent, entity, time, source hints)
3. Dekomponovat na sub-queries
4. Executovat paralelně
5. Rankovat a deduplikovat
6. Syntetizovat výsledky

**Filtrová syntax:** `from:`, `in:`, `after:`, `before:`, `type:`

**Ranking:** relevance, freshness, authority (official docs > wiki > chat), completeness.

### Digest (denní/týdenní přehled)

**Trigger:** "digest", "co se dělo", "shrnutí aktivit"

Highlights: action items, decisions, mentions. Grouped by topic/project.

---

## Další domény

### Finance (interní účetnictví)
**Plugin:** `anthropic-knowledge-work-plugins/finance/`
Skills: journal entry prep, reconciliation, financial statements, variance analysis, close management, audit support, SOX testing.

### Human Resources
**Plugin:** `anthropic-knowledge-work-plugins/human-resources/`
Skills: compensation analysis, offer drafting, interview prep, onboarding, org planning, performance reviews, recruiting pipeline.

### Marketing
**Plugin:** `anthropic-knowledge-work-plugins/marketing/`
Skills: content creation, campaign planning, competitive briefing, brand review, email sequences, SEO audit, performance reporting.

### Design
**Plugin:** `anthropic-knowledge-work-plugins/design/`
Skills: accessibility review, design critique, handoff, design system, research synthesis, user research, UX copy.

### Engineering
**Plugin:** `anthropic-knowledge-work-plugins/engineering/`
Skills: architecture, code review, debugging, deployment, documentation, incident response, standup, system design, tech debt, testing strategy.

### Operations
**Plugin:** `anthropic-knowledge-work-plugins/operations/`
Skills: capacity planning, change requests, compliance tracking, process docs, optimization, risk assessment, runbooks, status reports, vendor reviews.

---

## Plugin architektura

Všechny pluginy sdílejí stejnou strukturu:

```
plugin-name/
├── .claude-plugin/plugin.json     # Manifest
├── .mcp.json                      # Tool connections
├── commands/                      # Slash příkazy (explicitně vyvolané)
├── skills/                        # Domain knowledge (automaticky použité)
├── CONNECTORS.md                  # Dokumentace konektorů
└── README.md
```

### Instalace

```bash
# Klonovat celý balík
git clone https://github.com/anthropics/anthropic-knowledge-work-plugins.git

# Zkopírovat konkrétní plugin
cp -r anthropic-knowledge-work-plugins/sales .claude/plugins/

# Nebo přes marketplace
claude plugin marketplace add anthropics/knowledge-work-plugins
```

### Customizace

1. Přepsat konektory v `.mcp.json` na vaše nástroje
2. Přidat firemní kontext do skill souborů (terminologie, procesy)
3. Vytvořit `<plugin>.local.md` s organizačními specifiky
4. Upravit workflows podle reálných procesů týmu

**Žádná infrastruktura, žádné build kroky — jen markdown a JSON.**

---

## Jak najít správný skill pro úkol

Uživatel typicky popisuje **problém**, ne nástroj. Mapování:

| Uživatel říká | Hledej v |
|---------------|----------|
| "porovnej dva excely" | document-skills.md → Porovnání XLS |
| "vyčisti data v tabulce" | financial-workflows.md → Clean Data XLS |
| "postav DCF model" | financial-workflows.md → DCF Model |
| "zkontroluj smlouvu" | office-workflows.md → Legal → Contract Review |
| "napiš email klientovi" | office-workflows.md → Sales → Draft Outreach |
| "co se dělo za týden" | office-workflows.md → Enterprise Search → Digest |
| "analyzuj pipeline" | office-workflows.md → Sales → Pipeline Review |
| "napiš spec" | office-workflows.md → PM → Write Spec |
| "SQL dotaz na tržby" | office-workflows.md → Data → Write Query |
| "roztřiď support tickety" | office-workflows.md → Support → Ticket Triage |
| "GDPR compliance check" | office-workflows.md → Legal → Compliance Check |
| "konsoliduj kvartální reporty" | document-skills.md → Konsolidace XLS |

### Discovery postup

1. **Semantic search:** `python3 knowledge-base/tools/semantic-search.py "popis problému"`
2. **Routing tabulka:** Podívat se do CLAUDE.md na keyword → file mapping
3. **Knowledge graph:** `python3 knowledge-base/tools/discover.py related "téma"`
4. **Source repos:** Prohledat `knowledge-base/sources/` pro konkrétní skills a cookbooks
