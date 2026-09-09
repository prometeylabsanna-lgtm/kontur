from django.apps import AppConfig


class LandingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "landing"
    verbose_name = "Kontur+"

    def ready(self):
        from . import models_proxies  # noqa: F401
        from . import signals  # noqa: F401
