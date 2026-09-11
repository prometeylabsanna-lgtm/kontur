"""Django settings — Kontur+ landing."""

from pathlib import Path

from django.templatetags.static import static
from django.urls import reverse_lazy
from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

# Vercel sets VERCEL=1 on every deployment (Hobby included).
IS_VERCEL = config("VERCEL", default=False, cast=bool)

# Empty SECRET_KEY="" in the platform env would otherwise override the default.
_SECRET_FALLBACK = (
    "django-insecure-kontur-vercel-demo-7f3a9c2e1b8d4e6a0c5f"
    if IS_VERCEL
    else "django-insecure-dev-only-change-me"
)
SECRET_KEY = str(config("SECRET_KEY", default=_SECRET_FALLBACK) or "").strip() or _SECRET_FALLBACK

DEBUG = config("DEBUG", default=not IS_VERCEL, cast=bool)
ALLOWED_HOSTS = list(
    config(
        "ALLOWED_HOSTS",
        default="localhost,127.0.0.1,testserver",
        cast=Csv(),
    )
)
CSRF_TRUSTED_ORIGINS = list(
    config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
)

if IS_VERCEL:
    if ".vercel.app" not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(".vercel.app")
    _vercel_csrf = "https://*.vercel.app"
    if _vercel_csrf not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_vercel_csrf)

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
    "django.forms",
    "tinymce",
    "landing.apps.LandingConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# Custom admin widgets live under project templates/ — default DjangoTemplates
# form renderer only searches django/forms + app templates.
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

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

_database_url = config("DATABASE_URL", default="")
if _database_url:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(
            _database_url,
            conn_max_age=600,
            ssl_require=config("DATABASE_SSL_REQUIRE", default=False, cast=bool),
        )
    }
else:
    _sqlite_default = (
        "/tmp/kontur-vercel.sqlite3" if IS_VERCEL else str(BASE_DIR / "db.sqlite3")
    )
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": config("SQLITE_PATH", default=_sqlite_default),
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
LOCALE_PATHS = [BASE_DIR / "locale"]

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = Path("/tmp/kontur-staticfiles") if IS_VERCEL else (BASE_DIR / "staticfiles")
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedStaticFilesStorage"
        ),
    },
}

MEDIA_URL = "/media/"
_media_default = "/tmp/kontur-media" if IS_VERCEL else str(BASE_DIR / "media")
MEDIA_ROOT = Path(config("MEDIA_ROOT", default=_media_default))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Marketing analytics — load only after cookie consent ("Прийняти")
GTM_ID = config("GTM_ID", default="")
META_PIXEL_ID = config("META_PIXEL_ID", default="")

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

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
                {
                    "title": "Колір бренду",
                    "icon": "palette",
                    "link": reverse_lazy(
                        "admin:landing_brandcolorsettings_changelist"
                    ),
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
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/png",
            "href": lambda request: static("img/favicon-32x32.png"),
        },
        {
            "rel": "icon",
            "sizes": "16x16",
            "type": "image/png",
            "href": lambda request: static("img/favicon-16x16.png"),
        },
        {
            "rel": "apple-touch-icon",
            "sizes": "180x180",
            "type": "image/png",
            "href": lambda request: static("img/apple-touch-icon.png"),
        },
        {
            "rel": "shortcut icon",
            "type": "image/x-icon",
            "href": lambda request: static("img/favicon.ico"),
        },
    ],
    "COLORS": {
        "primary": {
            "50": "#f9f7f6",
            "100": "#f2f0ed",
            "200": "#e6e1dc",
            "300": "#d6cec6",
            "400": "#c6bbb0",
            "500": "#b0a091",
            "600": "#8e8277",
            "700": "#756c64",
            "800": "#605953",
            "900": "#4d4945",
            "950": "#383634",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "command_search": True,
        "show_all_applications": False,
        "navigation": _sidebar_navigation,
    },
}
