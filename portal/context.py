from django.urls import reverse, NoReverseMatch
from .models import AINastroj, AIPravidlo, AIZdroj


SITUACE_TILES = [
    {"label": "Chci přístup k AI nástroji", "icon": "key", "tone": "navy",
     "url_name": "portal:pristup",
     "desc": "Schvalovací proces, doba, podmínky."},
    {"label": "Chci vědět, co je OK a co ne", "icon": "rule", "tone": "navy",
     "url_name": "portal:pravidla",
     "desc": "Semafor pravidel a typů dat."},
    {"label": "Můžu nahrát citlivá data?", "icon": "shield", "tone": "navy",
     "url_name": "portal:data_matice",
     "desc": "Matice typů dat × nástrojů."},
    {"label": "Co bych mohl/a udělat s AI", "icon": "lightbulb", "tone": "amber",
     "url_name": "portal:use_cases",
     "desc": "Knihovna 10 use-cases s prompty."},
    {"label": "Jaké AI nástroje máme", "icon": "smart_toy", "tone": "navy",
     "url_name": "portal:nastroje",
     "desc": "Katalog schválených nástrojů."},
    {"label": "Chci se v AI naučit víc", "icon": "school", "tone": "navy",
     "url_name": "portal:vzdelavani",
     "desc": "Kurzy, platformy, slovník pojmů."},
    {"label": "Pro skeptiky", "icon": "psychology", "tone": "amber",
     "url_name": "portal:skeptik",
     "desc": "Pět use-cases, které fungují skoro vždy."},
    {"label": "Nevíte si rady?", "icon": "help", "tone": "navy",
     "url_name": "portal:faq",
     "desc": "FAQ — nejčastější otázky."},
]


MAIN_NAV = [
    {"label": "Nástroje", "url_name": "portal:nastroje"},
    {"label": "Use-cases", "url_name": "portal:use_cases"},
    {"label": "Novinky", "url_name": "portal:novinky_svet"},
    {"label": "Vzdělávání", "url_name": "portal:vzdelavani"},
    {"label": "Pravidla", "url_name": "portal:pravidla"},
]


def _resolve(items):
    out = []
    for it in items:
        try:
            url = reverse(it["url_name"])
        except NoReverseMatch:
            url = "#"
        out.append({**it, "url": url})
    return out


def site_globals(request):
    return {
        "MAIN_NAV": _resolve(MAIN_NAV),
        "SITUACE_TILES": _resolve(SITUACE_TILES),
        "STATS": {
            "nastroju": AINastroj.objects.filter(is_active=True).count(),
            "pravidel": AIPravidlo.objects.count(),
            "zdroju": AIZdroj.objects.count(),
        },
    }
