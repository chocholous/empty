# PPF Meet AI Portal

Django implementace interního AI portálu PPF — náhrada SharePoint webu MeetAI s vestavěným admin rozhraním.

## Tech stack

- **Django 5.1** — backend + ORM
- **django-unfold** — moderní admin UI v PPF brandu
- **TailwindCSS** (via CDN) — frontend styling
- **SQLite** — výchozí databáze (lze přepnout)

## Co portál obsahuje

12 stránek převzatých ze SharePoint exportu:

| Stránka | URL | Obsah |
|---|---|---|
| Homepage | `/` | Rozcestník 8 situací, statistiky, nejnovější novinky, slovníček |
| AI nástroje | `/nastroje/` | Katalog (27 nástrojů) s filtrem a hledáním |
| Use-cases | `/use-cases/` | Knihovna scénářů s hotovými prompty (10 položek) |
| Novinky — svět | `/novinky/` | Externí AI novinky |
| Novinky — PPF | `/novinky/ppf/` | Interní novinky |
| Pravidla | `/pravidla/` | Zásady ANO/POZOR/NE + semafor nástrojů |
| Vzdělávání | `/vzdelavani/` | 19 vzdělávacích zdrojů + slovníček (11 pojmů) |
| FAQ | `/faq/` | Nejčastější otázky (5) |
| Přístup | `/pristup/` | Žádost o přístup k nástroji |
| Data matice | `/data-matice/` | Matice typů dat × nástrojů |
| Pro skeptiky | `/skeptik/` | 5 use-cases s vysokou spolehlivostí |
| Admin panel | `/admin/` | Správa veškerého obsahu |

## Spuštění

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py import_sharepoint     # naimportuje data ze SharePoint exportu
python manage.py createsuperuser
python manage.py runserver
```

## Datové modely (odpovídají SharePoint listům)

- `AINastroj` ← AINastroje (27 položek)
- `AIPravidlo` ← AIPravidla (6 — semafor zelená/žlutá/červená)
- `AINovinka` ← AINovinky (interní + externí)
- `AIUseCase` ← AIUseCases (s FK na nástroj a M2M na alternativy)
- `AIZdroj` ← AIZdroje (vzdělávací materiály)
- `AISlovnicekTerm` ← AISlovnicek
- `AIFaqItem` ← AIFaq
- `Guide` ← Guides (vícesekcový průvodce)
- `Zasada` ← Zasady (ANO/POZOR/NE)
- `AIFeedback` ← AIFeedback (sběr zpětné vazby z frontendu)

## Admin

- Vestavěná správa všech 10 modelů přes django-unfold v PPF brandu (navy `#002c5a`)
- Semafor / barevné badge pro úroveň dat, semafor pravidel, spolehlivost use-cases
- Inline úprava `sort_order` přímo v seznamech
- Filtry a fulltext search v každém modelu
- Bočním menu odpovídá struktuře obsahu portálu

## Frontend

- PPF Navy `#002c5a` jako primární barva
- Krémový podklad `#f5f1ea`, akcentní písková `#ecd9b8`
- Inter font, Material Symbols ikony
- Responsivní layout (mobile + desktop)
- Feedback widget na každé stránce (zapisuje do `AIFeedback`)
