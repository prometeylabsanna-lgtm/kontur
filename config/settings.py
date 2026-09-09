"""Django settings — Kontur+ landing."""

from pathlib import Path

from django.urls import reverse_lazy
from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="django-insecure-dev-only-change-me")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,testserver",
    cast=Csv(),
)

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
    "tinymce",
    "landing.apps.LandingConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "landing.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

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

LANGUAGE_CODE = "uk"
TIME_ZONE = "Europe/Kyiv"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TINYMCE_DEFAULT_CONFIG = {
    "height": 360,
    "menubar": False,
    "plugins": "lists link code table",
    "toolbar": "undo redo | bold italic | bullist numlist | link | code",
    "content_style": "body { font-family: Outfit, sans-serif; font-size: 14px; }",
}


def _sidebar_navigation(request=None):
    from landing.site_content_registry import build_content_sidebar_items

    return [
        {
            "title": "Налаштування",
            "separator": True,
            "items": [
                {
                    "title": "Сайт",
                    "icon": "settings",
                    "link": reverse_lazy("admin:landing_sitesettings_changelist"),
                },
            ],
        },
        {
            "title": "Блоки сайту",
            "separator": True,
            "items": build_content_sidebar_items(),
        },
        {
            "title": "Заявки",
            "separator": True,
            "items": [
                {
                    "title": "Заявки з сайту",
                    "icon": "call",
                    "link": reverse_lazy("admin:landing_lead_changelist"),
                },
            ],
        },
    ]


UNFOLD = {
    "SITE_TITLE": "Kontur+",
    "SITE_HEADER": "Kontur+",
    "SITE_SYMBOL": "home_repair_service",
    "COLORS": {
        "primary": {
            "50": "oklch(98.6% .031 120.757)",
            "100": "oklch(96.7% .067 122.328)",
            "200": "oklch(93.8% .127 124.321)",
            "300": "oklch(89.7% .196 126.665)",
            "400": "oklch(84.1% .238 128.85)",
            "500": "oklch(76.8% .233 130.85)",
            "600": "oklch(64.8% .2 131.684)",
            "700": "oklch(53.2% .157 131.589)",
            "800": "oklch(45.3% .124 130.933)",
            "900": "oklch(40.5% .101 131.063)",
            "950": "oklch(27.4% .072 132.109)",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "command_search": True,
        "show_all_applications": False,
        "navigation": _sidebar_navigation,
    },
}
