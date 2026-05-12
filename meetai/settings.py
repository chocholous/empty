from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-8^d(zm6@-#f1d#$x=ovzqae9z_vst^u-@xh#ko)y@(vbq(6rc@"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "portal",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

# WhiteNoise is optional; remove from middleware if not installed
try:
    import whitenoise  # noqa: F401
except ImportError:
    MIDDLEWARE = [m for m in MIDDLEWARE if "whitenoise" not in m]

ROOT_URLCONF = "meetai.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "portal.context.site_globals",
            ],
        },
    },
]

WSGI_APPLICATION = "meetai.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "cs"
TIME_ZONE = "Europe/Prague"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# django-unfold — moderní admin v PPF brandu
UNFOLD = {
    "SITE_TITLE": "Meet AI · PPF",
    "SITE_HEADER": "Meet AI Admin",
    "SITE_SUBHEADER": "Správa portálu AI v PPF",
    "SITE_URL": "/",
    "SITE_SYMBOL": "smart_toy",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "THEME": "light",
    "COLORS": {
        "primary": {
            "50":  "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96  165 250",
            "500": "12  62  117",
            "600": "0   44  90",
            "700": "0   36  74",
            "800": "0   28  58",
            "900": "0   20  42",
            "950": "0   12  26",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Obsah portálu",
                "separator": True,
                "items": [
                    {"title": "Domů", "icon": "home", "link": "/admin/"},
                    {"title": "AI nástroje", "icon": "smart_toy",
                     "link": "/admin/portal/ainastroj/"},
                    {"title": "Use-cases", "icon": "lightbulb",
                     "link": "/admin/portal/aiusecase/"},
                    {"title": "Novinky", "icon": "newspaper",
                     "link": "/admin/portal/ainovinka/"},
                    {"title": "Pravidla (semafor)", "icon": "traffic",
                     "link": "/admin/portal/aipravidlo/"},
                    {"title": "Zásady (ANO/NE)", "icon": "rule",
                     "link": "/admin/portal/zasada/"},
                    {"title": "Vzdělávací zdroje", "icon": "school",
                     "link": "/admin/portal/aizdroj/"},
                    {"title": "Slovníček", "icon": "menu_book",
                     "link": "/admin/portal/aislovnicekterm/"},
                    {"title": "FAQ", "icon": "quiz",
                     "link": "/admin/portal/aifaqitem/"},
                    {"title": "Guides", "icon": "import_contacts",
                     "link": "/admin/portal/guide/"},
                ],
            },
            {
                "title": "Zpětná vazba",
                "separator": True,
                "items": [
                    {"title": "Feedback", "icon": "feedback",
                     "link": "/admin/portal/aifeedback/"},
                ],
            },
            {
                "title": "Systém",
                "separator": True,
                "items": [
                    {"title": "Uživatelé", "icon": "person",
                     "link": "/admin/auth/user/"},
                    {"title": "Skupiny", "icon": "group",
                     "link": "/admin/auth/group/"},
                ],
            },
        ],
    },
}
