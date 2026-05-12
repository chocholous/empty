"""Import all SharePoint list exports into Django models.

Each list JSON file (portal/data/<Name>.json) is parsed and items are
upserted by ``Id`` from the original SharePoint list. Tool icons referenced
from SharePoint are rewritten to local /static/img/tool-logos/ paths.
"""

import json
import re
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from portal.models import (
    AINastroj, AIPravidlo, AINovinka, AIUseCase, AIZdroj,
    AISlovnicekTerm, AIFaqItem, Guide, Zasada, AIFeedback,
)


DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _items(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    return raw.get("value") or raw.get("items") or []


def _dt(s):
    if not s:
        return timezone.now()
    parsed = parse_datetime(s)
    if parsed is None:
        return timezone.now()
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _rewrite_icon(url) -> str:
    if isinstance(url, dict):
        url = url.get("Url") or ""
    if not url:
        return ""
    m = re.search(r"tool-logos/([^/?#]+)", url)
    if m:
        return f"/static/img/tool-logos/{m.group(1)}"
    return url


def _link_pair(value):
    """SharePoint hyperlink fields are {'Url': ..., 'Description': ...}."""
    if isinstance(value, dict):
        return value.get("Description") or "", value.get("Url") or ""
    if isinstance(value, str):
        return "", value
    return "", ""


class Command(BaseCommand):
    help = "Import SharePoint Meet AI lists into Django"

    def add_arguments(self, parser):
        parser.add_argument("--wipe", action="store_true", help="Drop existing rows first")

    def handle(self, *args, wipe=False, **kw):
        if wipe:
            for M in [AIFeedback, Guide, AIFaqItem, AISlovnicekTerm, AIZdroj,
                      AIUseCase, AINovinka, AIPravidlo, Zasada, AINastroj]:
                M.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing rows deleted."))

        self.import_nastroje()
        self.import_pravidla()
        self.import_novinky()
        # Use-cases reference Nastroje, so import them after Nastroje
        self.import_use_cases()
        self.import_zdroje()
        self.import_slovnicek()
        self.import_faq()
        self.import_guides()
        self.import_zasady()
        self.import_feedback()

        self.stdout.write(self.style.SUCCESS("Import dokončen."))

    def import_nastroje(self):
        items = _items(DATA_DIR / "AINastroje.json")
        for it in items:
            pristup_label, pristup_url = _link_pair(it.get("LinkPristup"))
            navod_label, navod_url = _link_pair(it.get("LinkNavod"))
            data_level = (it.get("DataLevel") or "internal").lower()
            if data_level not in dict(AINastroj.DATA_LEVEL_CHOICES):
                data_level = "internal"
            AINastroj.objects.update_or_create(
                id=it["Id"],
                defaults=dict(
                    title=it.get("Title") or "",
                    kategorie=it.get("Kategorie") or "Ostatní",
                    kratky_popis=it.get("KratkyPopis") or "",
                    pouziti=it.get("Pouziti") or "",
                    limity=it.get("Limity") or "",
                    pristup=it.get("Pristup") or "",
                    ikona_url=_rewrite_icon(it.get("IkonaUrl") or ""),
                    link_pristup_label=pristup_label,
                    link_pristup_url=pristup_url,
                    link_navod_label=navod_label,
                    link_navod_url=navod_url,
                    data_level=data_level,
                    tagy=it.get("Tagy") or "",
                    sort_order=it.get("SortOrder") or 0,
                    is_active=bool(it.get("IsActive", True)),
                    modified=_dt(it.get("Modified")),
                    created=_dt(it.get("Created")),
                ),
            )
        self.stdout.write(f"AINastroje: {len(items)}")

    def import_pravidla(self):
        items = _items(DATA_DIR / "AIPravidla.json")
        for it in items:
            link1_label, link1_url = _link_pair(it.get("Link1Url"))
            level = (it.get("Level") or "green").lower()
            if level not in dict(AIPravidlo.LEVEL_CHOICES):
                level = "green"
            AIPravidlo.objects.update_or_create(
                id=it["Id"],
                defaults=dict(
                    title=it.get("Title") or "",
                    description=it.get("Description") or "",
                    level=level,
                    tool_name=it.get("ToolName") or "",
                    tool_icon=it.get("ToolIcon") or "",
                    link1_label=it.get("Link1Label") or link1_label,
                    link1_url=link1_url,
                    sort_order=it.get("SortOrder") or 0,
                    modified=_dt(it.get("Modified")),
                    created=_dt(it.get("Created")),
                ),
            )
        self.stdout.write(f"AIPravidla: {len(items)}")

    def import_novinky(self):
        items = _items(DATA_DIR / "AINovinky.json")
        for it in items:
            article_label, article_url = _link_pair(it.get("ArticleUrl"))
            link1_label_raw, link1_url = _link_pair(it.get("Link1Url"))
            link2_label_raw, link2_url = _link_pair(it.get("Link2Url"))
            AINovinka.objects.update_or_create(
                id=it["Id"],
                defaults=dict(
                    title=it.get("Title") or "",
                    perex=it.get("Perex") or "",
                    body=it.get("Body") or "",
                    category=it.get("Category") or "",
                    source=it.get("Source") or "Internal",
                    publish_date=_dt(it.get("PublishDate")),
                    article_label=it.get("Link1Label") and "" or article_label,
                    article_url=article_url,
                    link1_label=it.get("Link1Label") or link1_label_raw,
                    link1_url=link1_url,
                    link2_label=it.get("Link2Label") or link2_label_raw,
                    link2_url=link2_url,
                    sort_order=it.get("SortOrder") or 0,
                    is_active=bool(it.get("IsActive", True)),
                    modified=_dt(it.get("Modified")),
                    created=_dt(it.get("Created")),
                ),
            )
        self.stdout.write(f"AINovinky: {len(items)}")

    def import_use_cases(self):
        items = _items(DATA_DIR / "AIUseCases.json")
        for it in items:
            nastroj_id = it.get("NastrojIdId")
            nastroj = AINastroj.objects.filter(id=nastroj_id).first() if nastroj_id else None
            success = it.get("SuccessRate") or "Střední"
            if success not in dict(AIUseCase.RELIABILITY_CHOICES):
                success = "Střední"
            obj, _ = AIUseCase.objects.update_or_create(
                id=it["Id"],
                defaults=dict(
                    title=it.get("Title") or "",
                    cinnost=it.get("Cinnost") or "",
                    naklik=it.get("Naklik") or "",
                    postup=it.get("Postup") or "",
                    prompt=it.get("Prompt") or "",
                    nastroj=nastroj,
                    varovani=it.get("Varovani") or "",
                    ocekavany_vystup=it.get("OcekavanyVystup") or "",
                    kdyz_nefunguje=it.get("KdyzNefunguje") or "",
                    komu_napsat=it.get("KomuNapsat") or "",
                    success_rate=success,
                    gif_url=it.get("GifUrl") or "",
                    sort_order=it.get("SortOrder") or 0,
                    is_active=bool(it.get("IsActive", True)),
                    modified=_dt(it.get("Modified")),
                    created=_dt(it.get("Created")),
                ),
            )
            alt_ids = it.get("AlternativniNastrojeId") or []
            if alt_ids:
                obj.alternativy.set(AINastroj.objects.filter(id__in=alt_ids))
        self.stdout.write(f"AIUseCases: {len(items)}")

    def import_zdroje(self):
        items = _items(DATA_DIR / "AIZdroje.json")
        for it in items:
            url_label, url = _link_pair(it.get("Url"))
            category = it.get("Category") or "Kurz"
            AIZdroj.objects.update_or_create(
                id=it["Id"],
                defaults=dict(
                    title=it.get("Title") or "",
                    description=it.get("Description") or "",
                    category=category,
                    provider=it.get("Provider") or "",
                    url_label=url_label,
                    url=url,
                    icon_name=it.get("IconName") or "",
                    tags=it.get("Tags") or "",
                    sort_order=it.get("SortOrder") or 0,
                    modified=_dt(it.get("Modified")),
                    created=_dt(it.get("Created")),
                ),
            )
        self.stdout.write(f"AIZdroje: {len(items)}")

    def import_slovnicek(self):
        items = _items(DATA_DIR / "AISlovnicek.json")
        for it in items:
            label, url = _link_pair(it.get("LearnMoreUrl"))
            AISlovnicekTerm.objects.update_or_create(
                id=it["Id"],
                defaults=dict(
                    title=it.get("Title") or "",
                    definition=it.get("Definition") or "",
                    learn_more_label=label,
                    learn_more_url=url,
                    icon_name=it.get("IconName") or "",
                    sort_order=it.get("SortOrder") or 0,
                    modified=_dt(it.get("Modified")),
                    created=_dt(it.get("Created")),
                ),
            )
        self.stdout.write(f"AISlovnicek: {len(items)}")

    def import_faq(self):
        items = _items(DATA_DIR / "AIFaq.json")
        for it in items:
            label, url = _link_pair(it.get("LearnMoreUrl"))
            AIFaqItem.objects.update_or_create(
                id=it["Id"],
                defaults=dict(
                    title=it.get("Title") or "",
                    definition=it.get("Definition") or "",
                    learn_more_label=label,
                    learn_more_url=url,
                    icon_name=it.get("IconName") or "",
                    sort_order=it.get("SortOrder") or 0,
                    modified=_dt(it.get("Modified")),
                    created=_dt(it.get("Created")),
                ),
            )
        self.stdout.write(f"AIFaq: {len(items)}")

    def import_guides(self):
        items = _items(DATA_DIR / "Guides.json")
        for it in items:
            stype = (it.get("SectionType") or "section").lower()
            if stype not in dict(Guide.SECTION_CHOICES):
                stype = "section"
            status = it.get("Status") or "Published"
            if status not in dict(Guide.STATUS_CHOICES):
                status = "Published"
            Guide.objects.update_or_create(
                id=it["Id"],
                defaults=dict(
                    title=it.get("Title") or "",
                    title_en=it.get("TitleEN") or "",
                    guide_slug=it.get("GuideSlug") or "",
                    guide_name=it.get("GuideName") or "",
                    guide_name_en=it.get("GuideNameEN") or "",
                    section_type=stype,
                    content=it.get("Content") or "",
                    content_en=it.get("ContentEN") or "",
                    variant=it.get("Variant") or "",
                    image_url=it.get("ImageUrl") or "",
                    icon=it.get("Icon") or "",
                    status=status,
                    sort_order=it.get("SortOrder") or 0,
                    modified=_dt(it.get("Modified")),
                    created=_dt(it.get("Created")),
                ),
            )
        self.stdout.write(f"Guides: {len(items)}")

    def import_zasady(self):
        # SharePoint Zasady → category is one of ANO/POZOR/NE
        items = _items(DATA_DIR / "Zasady.json")
        for it in items:
            cat = (it.get("Category") or "ANO").upper()
            if cat not in dict(Zasada.CATEGORY_CHOICES):
                cat = "ANO"
            Zasada.objects.update_or_create(
                id=it["Id"],
                defaults=dict(
                    title=it.get("Title") or "",
                    description=it.get("Description") or "",
                    category=cat,
                    image_url=it.get("ImageUrl") or "",
                    sort_order=it.get("SortOrder") or 0,
                    modified=_dt(it.get("Modified")),
                    created=_dt(it.get("Created")),
                ),
            )
        self.stdout.write(f"Zasady: {len(items)}")

    def import_feedback(self):
        items = _items(DATA_DIR / "AIFeedback.json")
        for it in items:
            raw_score = it.get("Score")
            if isinstance(raw_score, int):
                score = "up" if raw_score > 0 else "down"
            else:
                score = (raw_score or "up").lower()
            if score not in dict(AIFeedback.SCORE_CHOICES):
                score = "up"
            AIFeedback.objects.update_or_create(
                id=it["Id"],
                defaults=dict(
                    title=it.get("Title") or "",
                    comment=it.get("Comment") or "",
                    page_url=it.get("PageUrl") or "",
                    score=score,
                    created=_dt(it.get("Created")),
                ),
            )
        self.stdout.write(f"AIFeedback: {len(items)}")
