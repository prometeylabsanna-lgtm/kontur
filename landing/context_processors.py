from django.conf import settings
from django.core.cache import cache

from .models import SiteBlock, SiteSettings

SITE_BLOCKS_CACHE_KEY = "kontur_site_blocks_v1"
SITE_BLOCKS_CACHE_TTL = 60


def _load_site_blocks() -> dict[str, SiteBlock]:
    cached = cache.get(SITE_BLOCKS_CACHE_KEY)
    if cached is not None:
        return cached
    blocks = {b.cache_key: b for b in SiteBlock.objects.all()}
    cache.set(SITE_BLOCKS_CACHE_KEY, blocks, SITE_BLOCKS_CACHE_TTL)
    return blocks


def site_context(request):
    settings_obj = SiteSettings.get_solo()
    return {
        "site_settings": settings_obj,
        "site_blocks": _load_site_blocks(),
        "SITE_PHONE_DISPLAY": settings_obj.phone_display or "+380 44 123 45 67",
        "SITE_PHONE_TEL": settings_obj.phone_tel or "+380441234567",
        "SITE_CITY": settings_obj.city or "Одеса",
        "SITE_HOURS": settings_obj.work_hours or "Пн–Сб · 09:00–19:00",
        "SITE_EMAIL": settings_obj.email or "hello@kontur.plus",
        "SITE_INSTAGRAM": settings_obj.instagram_url or "#",
        "SITE_TELEGRAM": settings_obj.telegram_url or "#",
        "SITE_NAME": settings_obj.site_name or "Kontur+",
        "SITE_BRAND_DESC": settings_obj.brand_desc or "ремонтна організація",
        "GTM_ID": getattr(settings, "GTM_ID", "") or "",
        "META_PIXEL_ID": getattr(settings, "META_PIXEL_ID", "") or "",
    }
