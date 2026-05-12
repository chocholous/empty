from django.db import models
from django.utils import timezone


class Ordered(models.Model):
    sort_order = models.IntegerField(default=0, verbose_name="Pořadí")
    is_active = models.BooleanField(default=True, verbose_name="Aktivní")
    modified = models.DateTimeField(default=timezone.now, verbose_name="Upraveno")
    created = models.DateTimeField(default=timezone.now, verbose_name="Vytvořeno")

    class Meta:
        abstract = True
        ordering = ["sort_order", "id"]


class AINastroj(Ordered):
    DATA_LEVEL_CHOICES = [
        ("green", "Zelená — OK i pro citlivá data"),
        ("yellow", "Žlutá — jen interní / veřejná"),
        ("red", "Červená — jen veřejná data"),
    ]
    title = models.CharField(max_length=200, verbose_name="Název")
    kategorie = models.CharField(max_length=50, default="Ostatní", verbose_name="Kategorie",
                                 help_text="Např. Copilot, Chat, Agent, Specializovaný, Vzdělávání")
    kratky_popis = models.TextField(verbose_name="Krátký popis")
    pouziti = models.TextField(blank=True, verbose_name="K čemu se hodí (HTML)")
    limity = models.TextField(blank=True, verbose_name="Limity a varování (HTML)")
    pristup = models.TextField(blank=True, verbose_name="Jak požádat o přístup (HTML)")
    ikona_url = models.CharField(max_length=300, blank=True, verbose_name="Cesta k ikoně")
    link_pristup_label = models.CharField(max_length=200, blank=True, verbose_name="Štítek odkazu — Přístup")
    link_pristup_url = models.URLField(blank=True, verbose_name="Odkaz — Přístup")
    link_navod_label = models.CharField(max_length=200, blank=True, verbose_name="Štítek odkazu — Návod")
    link_navod_url = models.URLField(blank=True, verbose_name="Odkaz — Návod")
    data_level = models.CharField(max_length=20, choices=DATA_LEVEL_CHOICES,
                                  default="yellow", verbose_name="Úroveň dat (semafor)")
    tagy = models.CharField(max_length=300, blank=True, verbose_name="Tagy (oddělené čárkami)")

    class Meta(Ordered.Meta):
        verbose_name = "AI nástroj"
        verbose_name_plural = "AI nástroje"

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return [t.strip() for t in self.tagy.split(",") if t.strip()]


class AIPravidlo(Ordered):
    LEVEL_CHOICES = [
        ("green", "Zelená — OK"),
        ("yellow", "Žlutá — pozor"),
        ("red", "Červená — zákaz"),
    ]
    title = models.CharField(max_length=200, verbose_name="Název pravidla")
    description = models.TextField(verbose_name="Popis / pro koho platí")
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default="green",
                             verbose_name="Semafor")
    tool_name = models.CharField(max_length=100, blank=True, verbose_name="Název nástroje")
    tool_icon = models.CharField(max_length=50, blank=True, verbose_name="Ikona nástroje")
    link1_label = models.CharField(max_length=200, blank=True, verbose_name="Štítek odkazu")
    link1_url = models.URLField(blank=True, verbose_name="Odkaz")

    class Meta(Ordered.Meta):
        verbose_name = "Pravidlo (semafor)"
        verbose_name_plural = "Pravidla (semafor)"

    def __str__(self):
        return f"{self.tool_name or self.title}"


class AINovinka(Ordered):
    SOURCE_CHOICES = [("Internal", "PPF (interní)"), ("External", "Svět (externí)")]
    title = models.CharField(max_length=300, verbose_name="Titulek")
    perex = models.TextField(verbose_name="Perex")
    body = models.TextField(blank=True, verbose_name="Tělo článku")
    category = models.CharField(max_length=100, blank=True, verbose_name="Kategorie")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="Internal",
                              verbose_name="Zdroj")
    publish_date = models.DateTimeField(default=timezone.now, verbose_name="Datum publikace")
    link1_label = models.CharField(max_length=200, blank=True, verbose_name="Odkaz 1 — štítek")
    link1_url = models.URLField(blank=True, verbose_name="Odkaz 1 — URL")
    link2_label = models.CharField(max_length=200, blank=True, verbose_name="Odkaz 2 — štítek")
    link2_url = models.URLField(blank=True, verbose_name="Odkaz 2 — URL")
    article_label = models.CharField(max_length=200, blank=True, verbose_name="Celý článek — štítek")
    article_url = models.URLField(blank=True, verbose_name="Celý článek — URL")

    class Meta:
        verbose_name = "Novinka"
        verbose_name_plural = "Novinky"
        ordering = ["-publish_date", "sort_order"]

    def __str__(self):
        return self.title


class AIUseCase(Ordered):
    RELIABILITY_CHOICES = [
        ("Vysoká", "Vysoká"),
        ("Střední", "Střední"),
        ("Nízká", "Nízká"),
    ]
    title = models.CharField(max_length=300, verbose_name="Název use-case")
    cinnost = models.CharField(max_length=100, verbose_name="Činnost (sumarizace, překlad, …)")
    naklik = models.TextField(verbose_name="Krátký popis / náklik")
    postup = models.TextField(blank=True, verbose_name="Postup (HTML)")
    prompt = models.TextField(blank=True, verbose_name="Hotový prompt")
    nastroj = models.ForeignKey(AINastroj, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="use_cases", verbose_name="Doporučený nástroj")
    alternativy = models.ManyToManyField(AINastroj, blank=True, related_name="alt_use_cases",
                                         verbose_name="Alternativní nástroje")
    varovani = models.TextField(blank=True, verbose_name="Varování / pozor na")
    ocekavany_vystup = models.TextField(blank=True, verbose_name="Očekávaný výstup")
    kdyz_nefunguje = models.TextField(blank=True, verbose_name="Když to nefunguje")
    komu_napsat = models.EmailField(blank=True, verbose_name="Komu napsat (e-mail)")
    success_rate = models.CharField(max_length=20, choices=RELIABILITY_CHOICES, default="Střední",
                                    verbose_name="Spolehlivost")
    gif_url = models.CharField(max_length=300, blank=True, verbose_name="URL ukázkového GIFu")

    class Meta(Ordered.Meta):
        verbose_name = "Use-case"
        verbose_name_plural = "Use-cases"

    def __str__(self):
        return self.title


class AIZdroj(Ordered):
    title = models.CharField(max_length=200, verbose_name="Název")
    description = models.TextField(verbose_name="Popis")
    category = models.CharField(max_length=50, default="Kurz", verbose_name="Kategorie",
                                help_text="Např. Kurz, Platform, Dokumentace, Návod, Agent")
    provider = models.CharField(max_length=200, blank=True, verbose_name="Provozovatel / autor")
    url_label = models.CharField(max_length=200, blank=True, verbose_name="Štítek odkazu")
    url = models.URLField(blank=True, verbose_name="URL")
    icon_name = models.CharField(max_length=50, blank=True, verbose_name="Material ikona")
    tags = models.CharField(max_length=300, blank=True, verbose_name="Tagy")

    class Meta(Ordered.Meta):
        verbose_name = "Vzdělávací zdroj"
        verbose_name_plural = "Vzdělávací zdroje"

    def __str__(self):
        return self.title


class AISlovnicekTerm(Ordered):
    title = models.CharField(max_length=100, verbose_name="Pojem")
    definition = models.TextField(verbose_name="Definice")
    learn_more_label = models.CharField(max_length=200, blank=True, verbose_name="Štítek odkazu")
    learn_more_url = models.URLField(blank=True, verbose_name="Odkaz — Více informací")
    icon_name = models.CharField(max_length=50, blank=True, verbose_name="Material ikona")

    class Meta(Ordered.Meta):
        verbose_name = "Pojem ve slovníčku"
        verbose_name_plural = "Slovníček (pojmy)"

    def __str__(self):
        return self.title


class AIFaqItem(Ordered):
    title = models.CharField(max_length=300, verbose_name="Otázka")
    definition = models.TextField(verbose_name="Odpověď")
    learn_more_label = models.CharField(max_length=200, blank=True, verbose_name="Štítek odkazu")
    learn_more_url = models.URLField(blank=True, verbose_name="Více informací — URL")
    icon_name = models.CharField(max_length=50, blank=True, verbose_name="Material ikona")

    class Meta(Ordered.Meta):
        verbose_name = "FAQ položka"
        verbose_name_plural = "FAQ"

    def __str__(self):
        return self.title


class Guide(Ordered):
    SECTION_CHOICES = [
        ("hero", "Hero (úvod)"),
        ("intro", "Intro odstavec"),
        ("section", "Sekce s nadpisem"),
        ("highlight", "Zvýrazněný box"),
        ("steps", "Kroky"),
        ("conclusion", "Závěr"),
    ]
    STATUS_CHOICES = [("Draft", "Koncept"), ("Published", "Publikováno")]
    title = models.CharField(max_length=200, verbose_name="Titulek")
    title_en = models.CharField(max_length=200, blank=True, verbose_name="Titulek (EN)")
    guide_slug = models.SlugField(max_length=100, verbose_name="Slug průvodce")
    guide_name = models.CharField(max_length=100, blank=True, verbose_name="Název průvodce")
    guide_name_en = models.CharField(max_length=100, blank=True, verbose_name="Název průvodce (EN)")
    section_type = models.CharField(max_length=20, choices=SECTION_CHOICES, default="section",
                                    verbose_name="Typ sekce")
    content = models.TextField(verbose_name="Obsah")
    content_en = models.TextField(blank=True, verbose_name="Obsah (EN)")
    variant = models.CharField(max_length=200, blank=True, verbose_name="Variant (kontext)")
    image_url = models.CharField(max_length=300, blank=True, verbose_name="URL obrázku")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Material ikona")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Published",
                              verbose_name="Stav")

    class Meta(Ordered.Meta):
        verbose_name = "Guide sekce"
        verbose_name_plural = "Guides — sekce průvodců"

    def __str__(self):
        return f"{self.guide_slug} · {self.title}"


class Zasada(Ordered):
    CATEGORY_CHOICES = [
        ("ANO", "ANO — jdi do toho"),
        ("POZOR", "POZOR — opatrně"),
        ("NE", "NE — radši ne"),
    ]
    title = models.CharField(max_length=200, verbose_name="Zásada")
    description = models.TextField(verbose_name="Popis")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default="ANO",
                                verbose_name="Typ")
    image_url = models.CharField(max_length=300, blank=True, verbose_name="URL obrázku")

    class Meta(Ordered.Meta):
        verbose_name = "Zásada AI"
        verbose_name_plural = "Zásady (ANO/POZOR/NE)"

    def __str__(self):
        return self.title


class AIFeedback(models.Model):
    SCORE_CHOICES = [
        ("up", "Pomohlo"),
        ("down", "Nepomohlo"),
    ]
    title = models.CharField(max_length=200, blank=True, verbose_name="Předmět")
    comment = models.TextField(blank=True, verbose_name="Komentář")
    page_url = models.CharField(max_length=300, blank=True, verbose_name="URL stránky")
    score = models.CharField(max_length=10, choices=SCORE_CHOICES, default="up",
                             verbose_name="Hodnocení")
    created = models.DateTimeField(default=timezone.now, verbose_name="Vytvořeno")

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback od uživatelů"
        ordering = ["-created"]

    def __str__(self):
        return f"{self.get_score_display()} · {self.page_url}"
