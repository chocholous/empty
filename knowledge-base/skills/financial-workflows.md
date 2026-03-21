# Financial Workflows — Skills pro finanční analýzu

## Přehled

56 production-ready skills z [anthropics/anthropic-financial-services-plugins](https://github.com/anthropics/anthropic-financial-services-plugins).
Pokrývají: financial analysis, investment banking, equity research, private equity, wealth management.

**Klíčový princip:** Všechny výstupy jsou Excel soubory s **formulemi** (nikdy hardcoded hodnoty). Každý hardcoded input má cell comment s citací zdroje.

## Instalace

```bash
# Claude Code
git clone https://github.com/anthropics/anthropic-financial-services-plugins.git
cp -r anthropic-financial-services-plugins/financial-analysis .claude/skills/

# Nebo celý plugin
claude plugin marketplace add anthropics/financial-services-plugins
```

## Excel pravidla (platí pro VŠECHNY financial skills)

### Formule, ne hodnoty
- **KRITICKÉ:** Každá odvozená buňka musí být Excel formule
- Nikdy nepočítejte v Pythonu a nevkládejte výsledek — vždy `=SUM()`, `=IF()`, atd.
- Po dokončení: `python scripts/recalc.py output.xlsx` (vyžaduje LibreOffice)

### Barevné kódování (IB standard)
| Barva textu | Význam |
|-------------|--------|
| Modrá (0,0,255) | Hardcoded inputs |
| Černá (0,0,0) | Formule a výpočty |
| Zelená (0,128,0) | Odkazy v rámci listu |
| Červená (255,0,0) | Externí odkazy |
| Žluté pozadí | Klíčové předpoklady |

### Formátování čísel
| Typ | Formát | Příklad |
|-----|--------|---------|
| Roky | Text string | "2024" (ne 2,024) |
| Měna | $#,##0 | $1,234 (jednotky v headers) |
| Nuly | Pomlčka | "-" |
| Procenta | 0.0% | 12.5% |
| Násobky | 0.0x | 8.5x (EV/EBITDA, P/E) |
| Záporné | Závorky | (1,234) ne -1,234 |

### Sensitivity tabulky
- Vždy **lichý** počet řádků/sloupců (5×5 nebo 7×7)
- Střed = base case (zvýrazněný)
- Conditionally formatted: zelená (accretive) → červená (dilutive)

---

## Comparable Company Analysis (Comps)

**Trigger:** "udělej comps", "srovnej firmy", "trading multiples", "peer analysis"

### Workflow
1. **Header block** — název analýzy, datum, měna, jednotky
2. **Operating Statistics** — Revenue, Revenue Growth, EBITDA, EBITDA Margin, EBIT pro každou firmu
3. **Valuation Multiples** — Market Cap, Enterprise Value, EV/Revenue, EV/EBITDA, P/E
4. **Statistics** — Max, 75th percentile, Median, 25th percentile, Min (jen pro poměrové metriky, ne absolutní)
5. **Notes** — metodologie, zdroje dat, datum cen

### Output
Excel s dvěma sekcemi (Operating + Valuation), statistiky pod každou sekcí.
Pravidlo "5-10" — max 5-10 comparable companies.

### Klíčová pravidla
- MCP zdroje dat první (Daloopa, FactSet, S&P), web search až jako fallback
- Cell comment na každém hardcoded inputu s citací
- Statistiky jen na ratios/margins, nikdy na absolutní metriky (revenue size)
- Ověřovat s uživatelem krok za krokem

---

## DCF Model

**Trigger:** "postav DCF", "discounted cash flow", "valuace firmy", "kolik firma stojí"

### Workflow
1. **Data** — Stáhnout financials (3-5 let historických dat)
2. **Revenue projekce** — 3 scénáře (Bear/Base/Bull)
3. **Operating expenses** — s operating leverage
4. **Unlevered FCF** — NOPAT + D&A - CapEx - delta NWC
5. **WACC** — přes CAPM (risk-free + beta × equity premium)
6. **Diskontování** — mid-year convention
7. **Terminal Value** — perpetuity growth NEBO exit multiple
8. **Bridge to equity** — EV - Net Debt = Equity Value ÷ shares = price/share
9. **Sensitivity tabulky** — 3 tabulky (WACC vs growth, WACC vs margin, WACC vs multiple)

### Klíčová pravidla
- Terminal growth < WACC (jinak model diverguje)
- Mid-year convention pro přesnější diskontování
- Sensitivity tabulky lichých rozměrů, střed = base case
- Zero formula errors před odevzdáním

---

## 3-Statement Model

**Trigger:** "trojvýkaz", "3-statement model", "propojený model", "integrovaný finanční model"

### Workflow
1. **Analyze template** — identifikovat taby (IS, BS, CF, Assumptions, Checks)
2. **Historická data** — vyplnit input buňky (Paste Values, respektovat sign conventions)
3. **Assumptions** — růstové drivery, marže, CapEx/Revenue, NWC days
4. **Projekce** — formule pro každou řádku (nikdy hardcoded)
5. **Cross-statement validace:**
   - BS Balance: Assets = Liabilities + Equity (v každém období)
   - Cash tie-out: CF ending cash = BS cash
   - NI link: IS Net Income = CF starting point
   - RE roll-forward: Opening RE + NI - Dividends = Closing RE

### Klíčová pravidla
- Nikdy nepřepisovat existující formule v template
- BS musí balancovat v každém období a scénáři
- Circular reference z úroků → zapnout iterative calculation
- Ověřovat výkaz po výkazu s uživatelem

---

## LBO Model

**Trigger:** "LBO", "leveraged buyout", "PE model", "návratnost investice"

### Workflow
1. **Sources & Uses** — jeden item je "plug" (balancující položka)
2. **Operating model** — P&L projekce z growth drivers
3. **Debt schedule** — úrok na beginning balance, cash sweep waterfall
4. **Returns** — IRR/MOIC se správnými znaménky cash flows
5. **Sensitivity** — Entry multiple vs Exit multiple, Leverage vs Growth

### Klíčová pravidla
- Úrok vždy na beginning balance (vyhnout se circular ref)
- Debt balances nemohou jít pod nulu (`MAX`/`MIN`)
- Cash sweep: senior → junior (waterfall)
- Vždy použít template pokud existuje

---

## Merger Model (Accretion/Dilution)

**Trigger:** "merger model", "accretion dilution", "M&A analýza", "akvizice dopad"

### Workflow
1. **Deal terms** — offer price, cash/stock mix, synergies, fees
2. **Purchase price** — premium, equity value, EV, implied multiples
3. **Sources & Uses** — new debt + cash + equity vs. purchase price + fees
4. **Pro Forma EPS** (Year 1-3) — combined NI + synergies - foregone interest - new interest - amortization
5. **Sensitivity** — accretion vs synergies/premium, vs cash/stock mix
6. **Breakeven synergies** — kolik synergií pro EPS-neutral Year 1

### Klíčová pravidla
- Vždy GAAP i adjusted (cash) EPS
- Synergy phase-in je kritický (Year 1 často jen 25-50% run-rate)
- Nezapomenout foregone interest na použitý cash
- Tax rate na adjustments = acquirer's marginal rate

---

## Audit XLS

**Trigger:** "zkontroluj spreadsheet", "audit model", "najdi chyby v excelu", "validace modelu"

### Co kontroluje
| Úroveň | Kontroly |
|---------|----------|
| **Formula** | #REF!, #DIV/0!, hardcodes uvnitř formulí, inconsistentní formule, off-by-one ranges |
| **Structural** | BS balance, CF tie-out, IS checks, circular refs |
| **Logic** | Sign conventions, unit mismatches, reasonableness |
| **Model-specific** | DCF: terminal growth < WACC. LBO: debt ≥ 0. Merger: share count. |

### Output
Tabulka findings: Severity (Critical/Warning/Info) | Sheet | Cell | Issue | Fix

### Klíčová pravidla
- BS balance je priorita #1
- Neměnit nic bez souhlasu — nejdřív report, pak fix
- Hardcoded overrides = hlavní zdroj tichých chyb

---

## Clean Data XLS

**Trigger:** "vyčisti data", "clean spreadsheet", "oprav excel", "standardizuj data"

### Co čistí
- Whitespace (trim)
- Casing (UPPER/lower/Title)
- Čísla jako text → skutečná čísla
- Nekonzistentní datumy → jednotný formát
- Duplikáty
- Prázdné buňky
- Smíšené typy v jednom sloupci

### Workflow
1. **Profile** — analyzovat každý sloupec (dominantní typ)
2. **Report** — tabulka: sloupec, problém, počet, navrhovaný fix
3. **Fix** — helper columns s formulemi (`=TRIM()`, `=VALUE()`) — ne přepis originálu
4. **Confirm** — kategorie po kategorii s potvrzením uživatele

### Klíčová pravidla
- Formule > hardcoded cleaned values (auditovatelnost)
- Nikdy nepřepisovat originál bez explicitního souhlasu
- Destruktivní operace (dedup, blank fill) potvrzovat

---

## Investment Banking Skills

### CIM Builder
**Trigger:** "CIM", "confidential information memorandum", "investor memo"
Workflow: Company overview → Industry → Financials → Growth → Investment highlights → Appendix

### Pitch Deck
**Trigger:** "pitch deck", "investor presentation"
Workflow: Situation overview → Strategic rationale → Valuation → Transaction structure → Next steps

### Buyer List
**Trigger:** "buyer list", "seznam kupujících", "potential acquirers"
Workflow: Strategic buyers → Financial sponsors → Screening criteria → Tiering

### Deal Tracker
**Trigger:** "deal tracker", "pipeline tracker"
Workflow: Deal pipeline s stages, probabilities, expected close dates

---

## Equity Research Skills

### Earnings Analysis
**Trigger:** "earnings", "výsledky hospodaření", "kvartální čísla"
Workflow: Beat/miss vs consensus → Segment breakdown → Guidance changes → Model impact → Rating implications

### Initiating Coverage
**Trigger:** "coverage initiation", "začít pokrývat firmu"
5 fází: Company research → Financial modeling → Valuation → Chart generation → Report assembly

### Morning Note
**Trigger:** "morning note", "ranní přehled"
Workflow: Overnight developments → Portfolio implications → Key events today

---

## Private Equity Skills

### Deal Screening
**Trigger:** "deal screening", "screening dealů", "ohodnoť tuto příležitost"
Workflow: Business quality → Financial profile → Market position → Key risks → Preliminary valuation

### IC Memo
**Trigger:** "IC memo", "investment committee memo"
Workflow: Executive summary → Business overview → Financial analysis → Returns analysis → Risks → Recommendation

### Unit Economics
**Trigger:** "unit economics", "jednotková ekonomika"
Workflow: Revenue per unit → COGS → Contribution margin → Payback period → LTV/CAC

---

## Wealth Management Skills

### Portfolio Rebalance
**Trigger:** "rebalancuj portfolio", "portfolio drift", "optimalizace alokace"
Workflow: Current allocation → Target deviation → Tax impact → Trade recommendations

### Financial Plan
**Trigger:** "finanční plán", "retirement planning", "plán do důchodu"
Workflow: Goals → Income/expenses → Gap analysis → Investment strategy → Projections

### Tax Loss Harvesting
**Trigger:** "tax loss harvesting", "daňová optimalizace"
Workflow: Identify losers → Wash sale check → Harvest candidates → Replacement securities

---

## MCP Data Sources

Finanční plugins podporují 11 MCP zdrojů:

| Zdroj | Data |
|-------|------|
| **Daloopa** | Standardized financials, KPIs |
| **FactSet** | Market data, estimates, fundamentals |
| **S&P Global** | Credit ratings, earnings, indices |
| **Morningstar** | Fund data, equity research |
| **LSEG (Refinitiv)** | Fixed income, FX, derivatives |
| **PitchBook** | PE/VC deals, valuations |
| **Moody's** | Credit analysis, default rates |
| **Bloomberg** | Terminal data (via MCP bridge) |
| **Capital IQ** | Screening, company data |
| **Visible Alpha** | Consensus estimates, detailed models |
| **AlphaSense** | Document search, transcripts |

Konfigurace v `.mcp.json`:
```json
{
  "connections": [
    {"name": "daloopa", "url": "https://mcp.daloopa.com/server/mcp"},
    {"name": "factset", "url": "https://mcp.factset.com/mcp"}
  ]
}
```
