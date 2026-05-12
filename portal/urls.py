from django.urls import path
from . import views

app_name = "portal"

urlpatterns = [
    path("", views.home, name="home"),
    path("nastroje/", views.nastroje, name="nastroje"),
    path("nastroje/<int:pk>/", views.nastroj_detail, name="nastroj_detail"),
    path("use-cases/", views.use_cases, name="use_cases"),
    path("use-cases/<int:pk>/", views.use_case_detail, name="use_case_detail"),
    path("novinky/", views.novinky_svet, name="novinky_svet"),
    path("novinky/ppf/", views.novinky_ppf, name="novinky_ppf"),
    path("novinky/<int:pk>/", views.novinka_detail, name="novinka_detail"),
    path("pravidla/", views.pravidla, name="pravidla"),
    path("vzdelavani/", views.vzdelavani, name="vzdelavani"),
    path("faq/", views.faq, name="faq"),
    path("pristup/", views.pristup, name="pristup"),
    path("data-matice/", views.data_matice, name="data_matice"),
    path("skeptik/", views.skeptik, name="skeptik"),
    path("guide/<slug:slug>/", views.guide_detail, name="guide"),
    path("feedback/", views.feedback_submit, name="feedback"),
]
