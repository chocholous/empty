---
id: related-parties-rkc
title: "RKC scope & Related Parties — data dictionary"
source_file: RelatedParties2026_Q1.xlsm
category: 01_Profile
refresh: quarterly
reporting_date: 2026-03-31
last_modified: 2026-04-02
live_source:
  drive_id: b!CJL9ke4ACUq11bSe5wR9OqXI0r8euv5HkCZj9xVatb-Nq4gvZp0YT5EI1nNtJeDN
  item_id: 01YWZEW33JGCNG7HBCYNAZG7BJPAU5BF23
  web_url: "https://ppfgroup-my.sharepoint.com/personal/soukupova_ppf_cz/Documents/Dokumenty/Cowork/Regulatory Skill Knowledge/01_Profile/RelatedParties2026_Q1.xlsm"
topics: [RKC scope, ownership %, consolidation method, related parties, LEI, org chart]
citation: "RelatedParties2026_Q1.xlsm (reporting 2026-03-31), KB 01_Profile/"
read_when: "Otázky 'kdo je v RKC scope?', 'jakou metodou konsolidujeme X?', ownership %, LEI, related parties."
---

# RKC scope & Related Parties — data dictionary

**Autoritativní operativní mapování** RKC scope a related parties. Toto je
**mapa listů** — ownership %, jména a metody čti **živě** z `live_source`
(kvartální soubor; čísla se sem nekopírují).

## Listy (sheet map)
| List | Obsah | Použij pro |
|---|---|---|
| **`CompaniesList`** | 13 entit s flagem `RKC=1` (Poseidon ID, akronym, jméno) | seznam RKC entit pro reporting — **bez PPF banky** (viz pozn.) |
| **`Slozeni RKC`** | 27 řádků — kompletní konsolidační scope vč. PPF banky a asociací: Poseidon ID, akronym, **direct/effective ownership %**, IČ, LEI, country, reporting currency, OrgChart Name, OrgChart Owner | **primární zdroj pro ownership %** a strukturu |
| **`RelatedParties`** | 554 řádků: ConsoID, EPIC, jméno, identifikátor, **Consolidation Method** (Full/Equity/No), **Prudential Consolidation** flag | „je entita X v plné konsolidaci?", „metoda konsolidace Y?" |
| `31-List`, `OtherLists`, `AMM_LCR_intragroup list`, `EPIC`, `GCC App` | podkladové pro RegPack šablony | referenčně |

## RKC scope — pravidlo počtu (DŮLEŽITÉ)
**14 entit v RKC** = **13** z `CompaniesList` (`RKC=1`) **+ PPF banka a.s.**
(`FHO_PPFB`). PPF banka **chybí** v `CompaniesList`, protože pro kvartální
reporting má samostatný balíček **„RegTables"** (ne RegPack) — ale **věcně JE
v RKC scope** (sedí s Profile.docx). Při dotazu „kdo je v RKC scope?" vždy uveď:
**13 z `CompaniesList` + PPF banka = 14**.

## Ownership % a consolidation method
→ **Nečti odsud, čti živě** z listu `Slozeni RKC` (ownership %) resp.
`RelatedParties` (consolidation method). Příklady polí, která list obsahuje:
direct vs effective ownership %, LEI, IČ, country, reporting currency.
*(Konkrétní procenta se v tomto datasetu záměrně neuvádějí — jsou kvartální a
důvěrná; cituj je přímo z živého souboru s reportingovým datem 2026-03-31.)*

## Pozn.
Profile.docx má jen **narativní výčet** entit (bez %). Pro jakékoli číselné/
strukturní detaily (kdo, kolik %, jaká metoda) je autoritativní **tento soubor**.
