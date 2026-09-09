"""Bootstrap Django on Vercel when Environment Variables UI is unavailable."""

from __future__ import annotations

_ready = False


def ensure_ready() -> None:
    """Migrate, collectstatic, and seed once per warm serverless instance."""
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
    _ready = True
