# Topic → Source Routing

Rychlá routovací tabulka pro agenta. Najdi téma → dostaneš **kartu datasetu**
(stabilní výklad) a/nebo **živý zdroj** (aktuální čísla). Vždy plať postup:
**1)** Profile pro kontext → **2)** rozhodnutí ČNB → **3)** metodika (interní
výklad) → **4)** reporty pro čísla (živě) → **5)** primární regulace
(EUR-Lex/EBA/ČNB, retrieve živě).

## Kontext & scope
| Otázka / téma | Karta | Živý zdroj |
|---|---|---|
| Profil PPF FH, supervize, struktura | `documents/01_profile.md` | 01_Profile.docx |
| Kdo je v RKC scope? (14 entit) | `documents/01_profile.md` + `reports/related_parties.md` | RelatedParties2026_Q1.xlsm |
| Ownership %, consolidation method, LEI | `reports/related_parties.md` | `Slozeni RKC` / `RelatedParties` |
| Účetní vs regulatorní scope | `documents/01_profile.md` | — |
| Kategorizace Large/Regular, J-SVI, O-SII | `documents/04_cnb_categorization_large_to_regular.md` | — |

## Kapitál & vlastní zdroje
| Téma | Karta (metodika/interní) | Živý zdroj (čísla) |
|---|---|---|
| Own funds CET1/AT1/T2 | `documents/03_methodology_GRC-2024-001.md` §5.1.1–5.1.4 | COREP `C_01.00`; Pillar3 `EU CC1` |
| CET1 deductions, prudential filters (AVA) | metodika §5.1.1.1–5.1.1.2 | — |
| Minority interest | metodika §5.1.4 | — |
| Kapitálové poměry (CET1/T1/Total ratio) | metodika „Required level" | COREP `C_03.00`; Pillar3 `EU KM1` |
| RWA / total risk exposure | metodika „Required level" | COREP `C_02.00.a`; Pillar3 `EU OV1` |
| Output floor | metodika §5.4.1 | COREP `C_02.00.b` |
| Buffery (CCoB, CCyB, SRB, O-SII) | metodika §5.3.1 | Pillar3 `EU KM1` |
| Pillar II requirement (P2R/SREP) | metodika §5.3.2 | — |
| DTA/DTL | metodika §5.1.1.2 | COREP `C_04.00` |
| Capital reconciliation (own funds ↔ rozvaha) | — | Pillar3 `EU CC2` |
| **Tier 2 — předčasné splacení / redemption** | `documents/04_cnb_decision_2026-063126_T2.md` | — (ČNB č.j. 2026/063126/CNB/580) |

## Rizika (RWA komponenty)
| Téma | Karta | Živý zdroj |
|---|---|---|
| Úvěrové riziko (STA, exposure classes) | metodika §5.4.1 | Pillar3 `EU CR*` |
| Credit Risk Mitigation (FCCM, netting) | metodika §5.4.1.3 | — |
| Counterparty Credit Risk (SA-CCR) | metodika §5.4.2 | — |
| Operační riziko (BIC) | metodika „Operational risk" | — |
| Tržní riziko (FX, position, commodity) | metodika „Market risk" | — |
| CVA | metodika „CVA" | — |

## Likvidita & leverage
| Téma | Karta | Živý zdroj |
|---|---|---|
| LCR | metodika „LCR" | Pillar3 `EU LIQ1`; KM1 |
| NSFR | metodika „NSFR" | Pillar3 `EU LIQ2`; KM1 |
| Leverage ratio | metodika „Leverage ratio" | Pillar3 `EU LR1/2/3`; COREP |

## Limity & expozice
| Téma | Karta | Živý zdroj |
|---|---|---|
| Large exposures (25 % T1) | metodika „Large exposure limits" | — |
| Investice mimo fin. sektor | metodika „Limits to investments…" | — |

## Resolution / BRRD / MREL
| Téma | Karta | Živý zdroj |
|---|---|---|
| BRRD recovery & resolution | metodika §6 | — |
| MREL (pozn.: aktuálně neaplikovatelný na PPF FH konsolidované úrovni) | metodika §5 + §6 | — |

## Reporting & disclosures
| Téma | Karta | Živý zdroj |
|---|---|---|
| FINREP (rozvaha, P&L) | `reports/finrep.md` | FINREP 2026-03-31 |
| COREP (kapitál, RWA, ratios) | `reports/corep.md` | COREP 2026-03-31 / 2025-12-31 |
| Pillar 3 disclosure | `reports/pillar3.md` + metodika „Disclosures" | Pillar III 4Q2025 |
| Regulatory reporting framework (ITS 2024/3117) | metodika „Regulatory reporting" | — |

## Mimo scope (skill `regulatory-advisor`)
AML/AMLR/AMLD6, DORA, MiCA, ESG/CSRD → mimo scope; odkázat na specialistu.

## ICAAP/ILAAP
| Téma | Stav |
|---|---|
| ICAAP/ILAAP Q1 2026 / Q4 2025 | **Šifrováno (MIP)** — nelze extrahovat; otevři v MS klientu. Viz `manifest.json`. |
