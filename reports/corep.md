---
id: corep
title: "COREP — sheet map / data dictionary"
category: "05_Disclosures / 06_Reports"
refresh: quarterly
sources:
  - id: corep-1q2026-report
    reporting_date: 2026-03-31
    priority: PRIMARY
    live_source:
      drive_id: b!CJL9ke4ACUq11bSe5wR9OqXI0r8euv5HkCZj9xVatb-Nq4gvZp0YT5EI1nNtJeDN
      item_id: 01YWZEW36TPSWPE2IUFRH3AMFQORGBPWMD
      web_url: "https://ppfgroup-my.sharepoint.com/personal/soukupova_ppf_cz/Documents/Dokumenty/Cowork/Regulatory Skill Knowledge/06_Reports/COREP 31032026.xlsx"
  - id: corep-4q2025-disclosures
    reporting_date: 2025-12-31
    priority: SECONDARY
    taxonomy: EBA COREP 4.0.0.0
    live_source:
      drive_id: b!CJL9ke4ACUq11bSe5wR9OqXI0r8euv5HkCZj9xVatb-Nq4gvZp0YT5EI1nNtJeDN
      item_id: 01YWZEW35EE7RY4RNLXFAJWHGO6UHWIK4V
      web_url: "https://ppfgroup-my.sharepoint.com/personal/soukupova_ppf_cz/Documents/Dokumenty/Cowork/Regulatory Skill Knowledge/05_Disclosures/10907718-EBA_COREP_4.0.0.0-corep_of-CON-20251231-001-export_for AI.xlsx"
topics: [own funds, RWA, capital ratios, output floor, memorandum items, "DTA/DTL"]
read_when: "Číselné otázky na kapitál (CET1/T1/Total), RWA, kapitálové poměry, output floor, surplus/deficit."
---

# COREP — sheet map / data dictionary

> **Čísla se sem nekopírují.** Tento soubor mapuje, **který COREP list** drží
> jakou metriku. Hodnotu vždy **čti živě** z příslušného souboru a **uveď
> reportingové datum** v citaci.

## Priorita zdrojů
1. **PRIMARY — `COREP 31032026.xlsx` (2026-03-31, 1Q2026)** v `06_Reports/`.
   Použij jako první pro nejaktuálnější čísla.
2. **SECONDARY — COREP CON 2025-12-31 (EBA 4.0.0.0)** v `05_Disclosures/`.
   Použij jen pokud 06_Reports údaj neobsahuje, nebo pro 4Q2025 srovnání.

## Template map (kde co je)
| COREP list | Obsah | Typické otázky |
|---|---|---|
| **C_01.00** | Own funds (CET1, AT1, T2, total own funds) | „kolik máme CET1 / T2 / total own funds?" |
| **C_02.00.a** | Total risk exposure amount (RWA) | „kolik je RWA?" |
| **C_02.00.b** | Own funds requirements + **output floor** | „jaké jsou kapitálové požadavky?", „output floor?" |
| **C_03.00** | Capital ratios — **CET1 / T1 / Total** | „jaká je CET1 ratio / total capital ratio?" |
| **C_04.00** | Memorandum items (vč. **DTA/DTL**) | „kolik DTA?", memorandum položky |

## Workflow
1. Identifikuj metriku → najdi list výše.
2. Načti **živě** PRIMARY zdroj (2026-03-31). Pokud tam metrika není, fallback
   na SECONDARY (2025-12-31).
3. Cituj: hodnota + list (např. `C_03.00`) + **reportingové datum**.
4. Nikdy nečísluj z hlavy ani z tohoto datasetu.
