# Deep Research task: Czech multi-floor apartment buildings with explicit Užitná plocha + per-floor plans

## Goal
Build a verification dataset of **Czech (preferably Prague) multi-floor apartment
buildings ("bytový dům" / "činžovní dům") published with both (a) an explicitly
labelled "Užitná plocha" (UP) in m² per ČSN 73 4055, and (b) raster floor-plan
images for multiple floors of that exact building.** I will use it to test
whether a vision-language model + classical CV pipeline can extract UP from raster
plans within ±10 % of the listed number.

## Hard filters (drop any candidate that fails)
1. **Multi-story:** ≥ 3 floors above ground, multi-unit residential. No single-family
   houses, no interiors, no commercial.
2. **Explicit "Užitná plocha" in m²** stated on a project page or PD title sheet.
   "Plocha" or "Area" without the qualifier is not enough — we've been burned by
   ambiguous fields meaning gross / footprint / per-floor at random.
3. **Per-floor půdorys images** (PNG/JPG ≥ 800×600 preferred, ≥ 400×300 acceptable)
   for at least 2 different floors of the building.
4. **License usable for research:** project pages, public PDs, public developer
   marketing OK. No gated databases, no paywalled images.
5. **Czech / Slovak preferred** (so ČSN/STN definitions apply); Praha strongly preferred.

## Sources worth trying (in priority order)
1. **archiweb.cz** — `/b/<slug>` project pages. About 30 % of multi-floor listings
   have "Užitná plocha" in the info card. We've already confirmed: Bytový dům
   Akcíz (Praha 2022, UP=527), Bytový dům Panorama Jih (Brno 2024, UP=5758),
   Žitný mlýn Boršov (2025, UP=15800). Crawl their "bytové domy" category for
   more.
2. **Czech developer marketing PDFs** — Trigema, JRD, Central Group, Finep,
   Skanska Reality, Crestyl, Penta Real Estate. Their pre-sale "prospekt" PDFs
   typically include floor plans of typical floors plus a building-totals table
   that names "celková užitná plocha" and per-apartment UP.
3. **archicakce.cz / earch.cz / e-architekt.cz** — smaller Czech architecture
   portals; may use the same project-card convention as archiweb.
4. **ČVUT FA / VUT FA / FUA TUL student diplomky** — published PDs (bachelor /
   master) on Dspace ČVUT etc. Usually have a full title block with UP, ZP, HPP.
5. **Profil zadavatele / e-zak.cz** — public procurement of new apartment
   buildings. Winning entries' PDs include UP tables. Slower but high quality.
6. **bezrealitky.cz** investment listings of whole buildings ("Bytový dům na
   prodej / celý dům"). Rare but UP is mandatory for the listing.
7. **Stavební úřad** archives (Prague has digitisation programmes for some
   districts). Hardest, but the most authoritative source — the stamped
   PD-stavební povolení.

## Output requested
A markdown list of **≥ 15 buildings** that pass all hard filters, with for each:
- Title + city + year
- Source URL (project page / PDF)
- Listed `užitná_plocha_m2` + `zastavěná_plocha_m2` + `hrubá_podlažní_plocha_m2`
  if also present + `počet_pater` + `počet_bytů`
- List of floor-plan image URLs with floor labels (1.PP, 1.NP, 2.NP, ...)
- One-sentence note on whether UP is "celkem za budovu", "per typical apartment",
  "per typical floor" — disambiguate the scope.

If fewer than 15 pass, return what you've got and a one-paragraph honest
explanation of where the gap is (e.g. "found 8, ran out of Praha-specific
listings with both UP and per-floor plans; developer PDFs give per-apartment UP
but not per-floor plans").

## What I already have (don't re-list)
- Bytový dům Akcíz (Praha 2022, archiweb.cz/b/bytovy-dum-akciz) UP=527, 3 plans
- Bytový dům Panorama Jih (Brno 2024, archiweb.cz/b/bytovy-dum-panorama-jih) UP=5758, 3 plans
- Žitný mlýn Boršov (2025, archiweb.cz/b/zitny-mlyn-borsov) UP=15800, 1 plan
- Iconik Apartments (Praha 2023, archdaily) GFA only, no UP
- Podun Apartment Building (Bratislava 2024, archdaily) ambiguous Area field

## Why this matters
The pipeline's correctness for UP depends entirely on the listed number being
unambiguous. ArchDaily's "Area" field was ambiguous for two of our cases (gross
for one, per-floor for the other) and cost a debugging round. We need a CZ/ČSN-
labelled GT.
