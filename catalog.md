# Catalog — zdroje KB

Lidsky čitelný index. Strojově: [`manifest.json`](manifest.json). Routing:
[`taxonomy.md`](taxonomy.md).

Legenda refresh: **static** (extrahováno do karty) · **quarterly** (čti živě) ·
**ongoing** (průběžně doplňováno) · **encrypted** (nečitelné).

| # | Zdroj | Kat. | Refresh | Repr. v datasetu | Datum |
|---|---|---|---|---|---|
| 1 | PPF FH Profile (`01_Profile.docx`) | 01_Profile | static | ✅ `documents/01_profile.md` | 2026-05-04 |
| 2 | RelatedParties (`RelatedParties2026_Q1.xlsm`) | 01_Profile | quarterly | 🗺️ `reports/related_parties.md` (mapa, bez čísel) | 2026-03-31 |
| 3 | ICAAP/ILAAP Q1 2026 | 02_ICAAP ILAAP | encrypted | ⛔ jen metadata | 2026-03-31 |
| 4 | ICAAP/ILAAP Q4 2025 | 02_ICAAP ILAAP | encrypted | ⛔ jen metadata | 2025-12-31 |
| 5 | GRC-2024-001 Group Framework v3.0 | 03_internal_methodologies | static | ✅ `documents/03_methodology_GRC-2024-001.md` | 2025-07-23 |
| 6 | ČNB svolení T2 (č.j. 2026/063126/CNB/580) | 04_CNB_decisions | ongoing | ✅ `documents/04_cnb_decision_2026-063126_T2.md` | 2026-04-27 |
| 7 | ČNB Large→Regular (oznámení) | 04_CNB_decisions | ongoing | ✅ `documents/04_cnb_categorization_large_to_regular.md` | 2026-01-23 |
| 8 | COREP CON 2025-12-31 (EBA 4.0.0.0) | 05_Disclosures | quarterly | 🗺️ `reports/corep.md` (sheet map) | 2025-12-31 |
| 9 | Pillar III 4Q2025 (114 listů) | 05_Disclosures | quarterly | 🗺️ `reports/pillar3.md` (table map) | 2025-12-31 |
| 10 | Pillar III PDF (reference) | 05_Disclosures | quarterly | 📎 jen metadata | 2025-06-30 |
| 11 | COREP 31032026 (**PRIMARY**) | 06_Reports | quarterly | 🗺️ `reports/corep.md` | 2026-03-31 |
| 12 | FINREP 31032026 (**PRIMARY**) | 06_Reports | quarterly | 🗺️ `reports/finrep.md` | 2026-03-31 |

## Pokrytí
- **Extrahováno (stabilní):** profil, metodika, 2× rozhodnutí ČNB — plný
  agent-friendly výklad v `documents/`.
- **Mapováno (kvartální, bez čísel):** RelatedParties, COREP, Pillar III,
  FINREP — sheet/table mapy + živé ukazatele v `reports/`.
- **Nepokryto:** 2× ICAAP/ILAAP (šifrováno MIP) — jen metadata.

## Pozn. k údržbě
Při kvartální obnově KB se mění obsah souborů 2, 8, 9, 11, 12 (ne struktura) —
karty v `reports/` zůstávají platné (jsou to mapy, ne hodnoty). Při **přidání
nového rozhodnutí ČNB** do `04_CNB_decisions/` přidej novou kartu do
`documents/` a položku do `manifest.json` + `taxonomy.md`.
