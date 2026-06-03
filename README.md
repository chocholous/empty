# Regulatory Knowledge Base — Agent Dataset (PPF Financial Holdings a.s.)

Agent-friendly přetavení sdílené OneDrive složky **„Regulatory Skill Knowledge"**
(vlastník: Lenka Soukupová, `soukupova@ppf.cz`) do strukturovaného datasetu
s metadaty, topic-routingem a citačními ukazateli. Účel: aby agent
(`regulatory-advisor`) odpovídal na regulatorní otázky **rychle a grounded**.

> **Stav:** vygenerováno 2026-06-03 z živé KB. Tento dataset je **indexní /
> metadatová vrstva + extrakt stabilního obsahu**, ne kompletní kopie zdrojů.

## Co tento dataset je (a co není)

| | |
|---|---|
| **Je** | Katalog zdrojů s metadaty (`manifest.json`), topic→zdroj routing (`taxonomy.md`), extrakt **stabilních** dokumentů (profil, metodika, rozhodnutí ČNB) do čistého Markdownu, a **datové slovníky / mapy listů** pro kvartální Excely (COREP, FINREP, Pillar III). |
| **Není** | Není dump důvěrných čísel. **Konkrétní kvartální finanční hodnoty** (kapitál CET1/T1/Total, RWA, ratios, expozice, FINREP položky) se sem **nekopírují** — zůstávají jako *ukazatele na živý zdroj*. Agent je čte živě z OneDrive (obnovují se kvartálně). |

Důvod hybridního přístupu: stabilní obsah (profil, metodika, individuální
rozhodnutí ČNB) se mění zřídka → vyplatí se ho extrahovat pro rychlý grounding.
Kvartální čísla rychle zastarají a jsou nejcitlivější → drží se živě.

## Jak to má agent používat

1. **Routing:** najdi téma v [`taxonomy.md`](taxonomy.md) → dostaneš ID zdroje
   a (u Excelů) konkrétní list/buňkovou oblast.
2. **Stabilní výklad:** čti kartu v [`documents/`](documents/) (profil, metodika,
   rozhodnutí ČNB) — má YAML frontmatter s metadaty a citacemi.
3. **Aktuální čísla:** v [`reports/`](reports/) najdi mapu listů a `live_source`
   (drive_id + item_id + web_url) → načti **živě** přes Microsoft Graph
   (`ReadFileContent`). Nikdy necituj číslo z tohoto datasetu jako aktuální.
4. **Citace:** každá karta i položka v `manifest.json` nese `citation` a
   `live_source` pro doložení odpovědi.

## Struktura

```
README.md            – tento přehled
manifest.json        – strojově čitelný katalog všech zdrojů KB (+ metadata)
taxonomy.md          – topic → zdroj routing (CRR/CRD/BRRD témata)
catalog.md           – lidsky čitelný index zdrojů
schema/
  document.schema.json – schéma položky manifestu / frontmatteru
documents/           – extrahovaný STABILNÍ obsah (karty)
  01_profile.md
  03_methodology_GRC-2024-001.md
  04_cnb_decision_2026-063126_T2.md
  04_cnb_categorization_large_to_regular.md
reports/             – datové slovníky / mapy listů (BEZ čísel) + live pointery
  related_parties.md
  corep.md
  pillar3.md
  finrep.md
```

## Zdrojová KB (živý zdroj)

- **drive_id:** `b!CJL9ke4ACUq11bSe5wR9OqXI0r8euv5HkCZj9xVatb-Nq4gvZp0YT5EI1nNtJeDN`
- **root:** `https://ppfgroup-my.sharepoint.com/personal/soukupova_ppf_cz/Documents/Dokumenty/Cowork/Regulatory%20Skill%20Knowledge`
- Pokud se `drive_id` změní (přesdílení/přesun), znovu jej získej otevřením
  root webUrl přes `GetDriveItem(web_url=...)`.

## Klasifikace a důvěrnost

Zdroje jsou **Non-Public / Confidential** (regulatorní data PPF FH). Tento
dataset záměrně **neobsahuje konkrétní kvartální finanční hodnoty**. Obsahuje
strukturu, metadata, výčet entit konsolidačního celku, vlastnické podíly a
fakta individuálních rozhodnutí ČNB (č.j., data, předmět) — tj. stabilní
„knowledge", nikoli citlivý balík čísel. Před jakýmkoli širším sdílením ověř
s vlastníkem KB (`soukupova@ppf.cz`) a klasifikací PPF.
