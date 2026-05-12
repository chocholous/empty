from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin, GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.models import User, Group
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeDateFilter
from unfold.decorators import display

from .models import (
    AINastroj, AIPravidlo, AINovinka, AIUseCase, AIZdroj,
    AISlovnicekTerm, AIFaqItem, Guide, Zasada, AIFeedback,
)

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(DjangoUserAdmin, ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(DjangoGroupAdmin, ModelAdmin):
    pass


@admin.register(AINastroj)
class AINastrojAdmin(ModelAdmin):
    list_display = ["title", "kategorie", "data_level", "is_active_badge", "sort_order"]
    list_editable = ["sort_order"]
    list_filter = ["kategorie", ("data_level", ChoicesDropdownFilter), "is_active"]
    search_fields = ["title", "kratky_popis", "tagy"]
    fieldsets = (
        ("Základ", {"fields": ("title", "kategorie", "kratky_popis", "ikona_url", "tagy")}),
        ("Obsah", {"fields": ("pouziti", "limity", "pristup")}),
        ("Přístup k nástroji", {"fields": ("link_pristup_label", "link_pristup_url",
                                            "link_navod_label", "link_navod_url")}),
        ("Klasifikace", {"fields": ("data_level", "sort_order", "is_active")}),
    )

    @display(description="Stav", boolean=True)
    def is_active_badge(self, obj):
        return obj.is_active


@admin.register(AIPravidlo)
class AIPravidloAdmin(ModelAdmin):
    list_display = ["tool_name", "title", "level_badge", "sort_order"]
    list_editable = ["sort_order"]
    list_filter = [("level", ChoicesDropdownFilter)]
    search_fields = ["title", "tool_name", "description"]

    @display(description="Semafor",
             label={"green": "success", "yellow": "warning", "red": "danger"})
    def level_badge(self, obj):
        return obj.level, obj.get_level_display()


@admin.register(AINovinka)
class AINovinkaAdmin(ModelAdmin):
    list_display = ["title", "source_badge", "category", "publish_date"]
    list_filter = [("source", ChoicesDropdownFilter), ("publish_date", RangeDateFilter)]
    search_fields = ["title", "perex", "body"]
    date_hierarchy = "publish_date"
    fieldsets = (
        ("Základ", {"fields": ("title", "category", "source", "publish_date", "is_active")}),
        ("Obsah", {"fields": ("perex", "body")}),
        ("Odkazy", {"fields": ("article_label", "article_url",
                                "link1_label", "link1_url", "link2_label", "link2_url")}),
        ("Pořadí", {"fields": ("sort_order",)}),
    )

    @display(description="Zdroj", label={"Internal": "info", "External": "warning"})
    def source_badge(self, obj):
        return obj.source, obj.get_source_display()


@admin.register(AIUseCase)
class AIUseCaseAdmin(ModelAdmin):
    list_display = ["title", "cinnost", "success_badge", "nastroj", "sort_order"]
    list_filter = ["cinnost", ("success_rate", ChoicesDropdownFilter), "nastroj"]
    search_fields = ["title", "naklik", "prompt"]
    autocomplete_fields = ["nastroj", "alternativy"]
    fieldsets = (
        ("Základ", {"fields": ("title", "cinnost", "naklik", "success_rate")}),
        ("Postup a prompt", {"fields": ("postup", "prompt", "ocekavany_vystup")}),
        ("Nástroje", {"fields": ("nastroj", "alternativy")}),
        ("Co když", {"fields": ("varovani", "kdyz_nefunguje", "komu_napsat")}),
        ("Multimédia", {"fields": ("gif_url",)}),
        ("Pořadí", {"fields": ("sort_order", "is_active")}),
    )

    @display(description="Spolehlivost",
             label={"Vysoká": "success", "Střední": "warning", "Nízká": "danger"})
    def success_badge(self, obj):
        return obj.success_rate, obj.success_rate


@admin.register(AIZdroj)
class AIZdrojAdmin(ModelAdmin):
    list_display = ["title", "category", "provider", "sort_order"]
    list_filter = ["category", "provider"]
    search_fields = ["title", "description", "tags", "provider"]


@admin.register(AISlovnicekTerm)
class AISlovnicekTermAdmin(ModelAdmin):
    list_display = ["title", "sort_order"]
    list_editable = ["sort_order"]
    search_fields = ["title", "definition"]


@admin.register(AIFaqItem)
class AIFaqItemAdmin(ModelAdmin):
    list_display = ["title", "sort_order"]
    list_editable = ["sort_order"]
    search_fields = ["title", "definition"]


@admin.register(Guide)
class GuideAdmin(ModelAdmin):
    list_display = ["guide_slug", "title", "section_type", "status", "sort_order"]
    list_filter = [("section_type", ChoicesDropdownFilter),
                   ("status", ChoicesDropdownFilter), "guide_slug"]
    search_fields = ["guide_slug", "title", "content"]


@admin.register(Zasada)
class ZasadaAdmin(ModelAdmin):
    list_display = ["title", "category_badge", "sort_order"]
    list_filter = [("category", ChoicesDropdownFilter)]
    search_fields = ["title", "description"]

    @display(description="Typ",
             label={"ANO": "success", "POZOR": "warning", "NE": "danger"})
    def category_badge(self, obj):
        return obj.category, obj.get_category_display()


@admin.register(AIFeedback)
class AIFeedbackAdmin(ModelAdmin):
    list_display = ["score_badge", "page_url", "title", "created"]
    list_filter = [("score", ChoicesDropdownFilter), ("created", RangeDateFilter)]
    search_fields = ["title", "comment", "page_url"]
    readonly_fields = ["created"]

    @display(description="Hodnocení", label={"up": "success", "down": "danger"})
    def score_badge(self, obj):
        return obj.score, obj.get_score_display()
