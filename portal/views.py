from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from collections import OrderedDict

from .models import (
    AINastroj, AIPravidlo, AINovinka, AIUseCase, AIZdroj,
    AISlovnicekTerm, AIFaqItem, Guide, Zasada, AIFeedback,
)


HERO_BY_PAGE = {
    "home":         {"eyebrow": "PPF MEET AI",
                     "heading": "AI v PPF na jednom místě",
                     "subheading": "Vyberte, co právě řešíte — najdete nástroje, pravidla, use-cases i vzdělání."},
    "nastroje":     {"eyebrow": "Katalog",
                     "heading": "Jaké AI nástroje máme",
                     "subheading": "Vyberte podle úkolu, ne podle značky. Každá karta vám řekne, k čemu se hodí a kde má hranice."},
    "use_cases":    {"eyebrow": "Knihovna",
                     "heading": "Co bych mohl/a udělat s AI",
                     "subheading": "Konkrétní scénáře s hotovými prompty na copy-paste a doporučeným nástrojem."},
    "novinky_ppf":  {"eyebrow": "Aktuality",
                     "heading": "Co je nového v AI v PPF",
                     "subheading": "Interní novinky, piloty a use-cases z PPF skupiny."},
    "novinky_svet": {"eyebrow": "Aktuality",
                     "heading": "Co je nového ve světě AI",
                     "subheading": "Externí novinky filtrované AI týmem — jen to, co dává smysl pro PPF."},
    "pravidla":     {"eyebrow": "Pravidla",
                     "heading": "Zásady používání AI v PPF",
                     "subheading": "Lidsky a srozumitelně — co je v pořádku, co raději ne, a proč."},
    "vzdelavani":   {"eyebrow": "Vzdělávání",
                     "heading": "Chci se v AI naučit víc",
                     "subheading": "Kurzy, platformy, slovník pojmů — Aibility, Claude 101, AI Fluency a další."},
    "faq":          {"eyebrow": "FAQ",
                     "heading": "Nevíte si rady?",
                     "subheading": "Nejčastější otázky o AI v PPF — přístupy, data, konzultace, školení."},
    "pristup":      {"eyebrow": "Přístup",
                     "heading": "Chci přístup k AI nástroji",
                     "subheading": "Jak požádat, kdo schvaluje a za jak dlouho."},
    "data_matice":  {"eyebrow": "Citlivá data",
                     "heading": "Můžu nahrát citlivá data?",
                     "subheading": "Matice typů dat × nástrojů — semafor pro každou kombinaci."},
    "skeptik":      {"eyebrow": "Pro skeptiky",
                     "heading": "Začněte tady — funguje skoro vždy",
                     "subheading": "Pět use-cases, kde AI klape spolehlivě. Bez marketingu, jen co reálně funguje."},
}


RELATED = {
    "home": [],
    "nastroje": [
        ("portal:pristup", "Jak požádat", "Schvalovací proces, doba, podmínky."),
        ("portal:use_cases", "Co s ním dělat", "Knihovna 10 use-cases."),
        ("portal:data_matice", "Co tam smím dát?", "Matice typů dat × nástrojů."),
    ],
    "use_cases": [
        ("portal:pristup", "Nemáte ještě nástroj?", "Žádost o přístup za pár dní."),
        ("portal:nastroje", "Detail nástrojů", "Microsoft Copilot, Claude, DeepL — co k čemu."),
        ("portal:skeptik", "Začněte jednoduše", "Pět use-cases pro skeptiky."),
    ],
    "novinky_ppf": [
        ("portal:novinky_svet", "Co je nového ve světě", "Externí AI novinky filtrované AI týmem."),
        ("portal:use_cases", "Vyzkoušejte", "Knihovna use-cases s hotovými prompty."),
        ("portal:skeptik", "Začněte jednoduše", "Pět use-cases pro skeptiky."),
    ],
    "novinky_svet": [
        ("portal:novinky_ppf", "Co je nového v PPF", "Interní novinky o AI u nás."),
        ("portal:use_cases", "Vyzkoušejte, co je nového", "Knihovna use-cases s prompty."),
        ("portal:nastroje", "Které nástroje můžete použít", "Katalog AI nástrojů."),
    ],
    "pravidla": [
        ("portal:data_matice", "Můžu nahrát citlivá data?", "Matice typů dat × nástrojů."),
        ("portal:nastroje", "Jaké AI nástroje máme", "Katalog a jak o přístup požádat."),
        ("portal:vzdelavani", "Chci se naučit víc", "Kurzy, platformy, slovník pojmů."),
    ],
    "vzdelavani": [
        ("portal:use_cases", "Co bych mohl/a udělat s AI", "Knihovna use-cases podle činnosti."),
        ("portal:pravidla", "Co je OK a co ne", "Zásady používání AI v PPF."),
        ("portal:skeptik", "Pro skeptiky", "Pět use-cases, které fungují skoro vždy."),
    ],
    "faq": [
        ("portal:nastroje", "Jaké nástroje máme", "Katalog schválených AI nástrojů."),
        ("portal:use_cases", "Co s nimi dělat", "Knihovna use-cases podle činnosti."),
        ("portal:data_matice", "Co s citlivými daty?", "Matice typů dat × nástrojů."),
    ],
    "pristup": [
        ("portal:use_cases", "Co s nástrojem dělat", "Knihovna use-cases podle činnosti."),
        ("portal:nastroje", "Přehled všech nástrojů", "Co se hodí k čemu, co naopak nehodí."),
        ("portal:data_matice", "Co s ním smím dělat?", "Matice typů dat × nástrojů."),
    ],
    "data_matice": [
        ("portal:nastroje", "Vyberte nástroj", "Najděte ten s odpovídající úrovní dat."),
        ("portal:pristup", "Žádost o přístup", "Pokud nástroj ještě nemáte."),
        ("portal:use_cases", "Konkrétní postupy", "Use-cases s varováním pro citlivá data."),
    ],
    "skeptik": [
        ("portal:use_cases", "Hlubší knihovna use-cases", "10 scénářů s prompty a postupy."),
        ("portal:nastroje", "Co všechno máme k dispozici", "Katalog schválených AI nástrojů."),
        ("portal:novinky_ppf", "Co se daří kolegům", "Interní novinky o AI v PPF."),
    ],
}


def _ctx(page_key, extra=None):
    ctx = {
        "page_key": page_key,
        "hero": HERO_BY_PAGE.get(page_key, {}),
        "related": RELATED.get(page_key, []),
    }
    if extra:
        ctx.update(extra)
    return ctx


def home(request):
    novinky = AINovinka.objects.filter(is_active=True).order_by("-publish_date")[:3]
    terms = AISlovnicekTerm.objects.filter(is_active=True)[:7]
    return render(request, "portal/home.html", _ctx("home", {
        "novinky": novinky,
        "terms": terms,
    }))


def nastroje(request):
    q = request.GET.get("q", "").strip()
    kategorie = request.GET.get("k", "")
    qs = AINastroj.objects.filter(is_active=True)
    if q:
        qs = qs.filter(title__icontains=q) | qs.filter(kratky_popis__icontains=q) | qs.filter(tagy__icontains=q)
    if kategorie:
        qs = qs.filter(kategorie=kategorie)
    kategorie_set = AINastroj.objects.values_list("kategorie", flat=True).distinct().order_by("kategorie")
    return render(request, "portal/nastroje.html", _ctx("nastroje", {
        "nastroje": qs,
        "q": q,
        "active_kategorie": kategorie,
        "kategorie_list": [k for k in kategorie_set if k],
    }))


def nastroj_detail(request, pk):
    obj = get_object_or_404(AINastroj, pk=pk, is_active=True)
    related_uc = AIUseCase.objects.filter(nastroj=obj, is_active=True)[:6]
    return render(request, "portal/nastroj_detail.html", _ctx("nastroje", {
        "nastroj": obj,
        "use_cases": related_uc,
    }))


def use_cases(request):
    cinnost = request.GET.get("c", "")
    qs = AIUseCase.objects.filter(is_active=True).select_related("nastroj")
    if cinnost:
        qs = qs.filter(cinnost=cinnost)
    cinnosti = AIUseCase.objects.values_list("cinnost", flat=True).distinct().order_by("cinnost")
    return render(request, "portal/use_cases.html", _ctx("use_cases", {
        "use_cases": qs,
        "active_cinnost": cinnost,
        "cinnost_list": [c for c in cinnosti if c],
    }))


def use_case_detail(request, pk):
    obj = get_object_or_404(AIUseCase, pk=pk, is_active=True)
    return render(request, "portal/use_case_detail.html", _ctx("use_cases", {"uc": obj}))


def novinky_ppf(request):
    items = AINovinka.objects.filter(is_active=True, source="Internal").order_by("-publish_date")
    return render(request, "portal/novinky.html", _ctx("novinky_ppf", {"novinky": items}))


def novinky_svet(request):
    items = AINovinka.objects.filter(is_active=True, source="External").order_by("-publish_date")
    return render(request, "portal/novinky.html", _ctx("novinky_svet", {"novinky": items}))


def novinka_detail(request, pk):
    obj = get_object_or_404(AINovinka, pk=pk, is_active=True)
    page_key = "novinky_ppf" if obj.source == "Internal" else "novinky_svet"
    return render(request, "portal/novinka_detail.html", _ctx(page_key, {"novinka": obj}))


def pravidla(request):
    zasady = Zasada.objects.filter(is_active=True)
    zasady_by_cat = OrderedDict()
    for cat, _label in Zasada.CATEGORY_CHOICES:
        items = [z for z in zasady if z.category == cat]
        if items:
            zasady_by_cat[cat] = items
    return render(request, "portal/pravidla.html", _ctx("pravidla", {
        "pravidla": AIPravidlo.objects.filter(is_active=True),
        "zasady_by_cat": zasady_by_cat,
    }))


def vzdelavani(request):
    cat = request.GET.get("k", "")
    qs = AIZdroj.objects.filter(is_active=True)
    if cat:
        qs = qs.filter(category=cat)
    cats = AIZdroj.objects.values_list("category", flat=True).distinct().order_by("category")
    return render(request, "portal/vzdelavani.html", _ctx("vzdelavani", {
        "zdroje": qs,
        "terms": AISlovnicekTerm.objects.filter(is_active=True),
        "active_kategorie": cat,
        "kategorie_list": [c for c in cats if c],
    }))


def faq(request):
    return render(request, "portal/faq.html", _ctx("faq", {
        "faq_items": AIFaqItem.objects.filter(is_active=True),
    }))


def pristup(request):
    return render(request, "portal/pristup.html", _ctx("pristup", {
        "nastroje": AINastroj.objects.filter(is_active=True),
    }))


def data_matice(request):
    DATA_TYPES = [
        ("public", "Veřejná data"),
        ("internal", "Interní data PPF"),
        ("confidential", "Důvěrná / klientská"),
        ("personal", "Osobní údaje (GDPR)"),
    ]
    # data_level semafor → výchozí riziko pro jednotlivé typy dat
    LEVEL_FOR = {
        "green":  {"public": "ok",   "internal": "ok",   "confidential": "ok",   "personal": "warn"},
        "yellow": {"public": "ok",   "internal": "ok",   "confidential": "warn", "personal": "no"},
        "red":    {"public": "ok",   "internal": "warn", "confidential": "no",   "personal": "no"},
    }
    tools = AINastroj.objects.filter(is_active=True).order_by("sort_order")[:8]
    matrix = []
    for tool in tools:
        row = {"tool": tool, "cells": []}
        for dkey, dlabel in DATA_TYPES:
            level = LEVEL_FOR.get(tool.data_level, LEVEL_FOR["yellow"]).get(dkey, "warn")
            row["cells"].append({"data_key": dkey, "data_label": dlabel, "level": level})
        matrix.append(row)
    return render(request, "portal/data_matice.html", _ctx("data_matice", {
        "data_types": DATA_TYPES,
        "matrix": matrix,
    }))


def skeptik(request):
    qs = AIUseCase.objects.filter(is_active=True, success_rate="Vysoká").select_related("nastroj")[:5]
    return render(request, "portal/skeptik.html", _ctx("skeptik", {"use_cases": qs}))


def guide_detail(request, slug):
    from django.http import Http404
    sections = Guide.objects.filter(guide_slug=slug, status="Published").order_by("sort_order")
    if not sections.exists():
        raise Http404("Průvodce nenalezen")
    return render(request, "portal/guide.html", _ctx("home", {
        "sections": sections,
        "guide_name": sections[0].guide_name,
        "guide_title": sections[0].title,
    }))


@require_POST
def feedback_submit(request):
    AIFeedback.objects.create(
        score=request.POST.get("score", "up"),
        comment=request.POST.get("comment", "")[:5000],
        page_url=request.POST.get("page_url", "")[:300],
        title=request.POST.get("page_title", "")[:200],
    )
    messages.success(request, "Děkujeme za zpětnou vazbu!")
    return redirect(request.POST.get("page_url") or "portal:home")
