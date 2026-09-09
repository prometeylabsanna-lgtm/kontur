"""Bootstrap Django on Vercel when Environment Variables UI is unavailable."""

from __future__ import annotations

_ready = False

_DEMO_USERNAME = "admin"
_DEMO_PASSWORD = "admin"
_DEMO_EMAIL = "admin@kontur.plus"


def ensure_demo_superuser() -> None:
    """Create or reset demo staff user for test deploys without env/CLI."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user, created = User.objects.get_or_create(
        username=_DEMO_USERNAME,
        defaults={
            "email": _DEMO_EMAIL,
            "is_staff": True,
            "is_superuser": True,
        },
    )
    if not created:
        user.email = _DEMO_EMAIL
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
    user.set_password(_DEMO_PASSWORD)
    user.save()


def ensure_ready() -> None:
    """Migrate, collectstatic, seed, and demo admin once per warm instance."""
    global _ready
    if _ready:
        return

    from django.conf import settings
    from django.core.management import call_command

    if not getattr(settings, "IS_VERCEL", False):
        _ready = True
        return

    call_command("migrate", interactive=False, verbosity=0)
    call_command("collectstatic", interactive=False, verbosity=0)
    call_command("seed_cms_content", verbosity=0)
    ensure_demo_superuser()
    _ready = True
