from __future__ import annotations

from django import template
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.html import escape
from django.utils.safestring import mark_safe

from landing.block_defaults import BLOCK_DEFAULTS
from landing.models import SiteBlock
from landing.responsive_images import (
    CARD_DEFAULT_W,
    CARD_QUALITY,
    CARD_SIZES,
    CARD_WIDTHS,
    HERO_DEFAULT_W,
    HERO_QUALITY,
    HERO_SIZES,
    HERO_WIDTHS,
    SECTION_DEFAULT_W,
    SECTION_QUALITY,
    SECTION_SIZES,
    SECTION_WIDTHS,
    responsive_src,
    responsive_srcset,
    static_webp_candidate,
)

register = template.Library()

_PRESET = {
    "hero": (HERO_WIDTHS, HERO_DEFAULT_W, HERO_QUALITY, HERO_SIZES),
    "section": (SECTION_WIDTHS, SECTION_DEFAULT_W, SECTION_QUALITY, SECTION_SIZES),
    "card": (CARD_WIDTHS, CARD_DEFAULT_W, CARD_QUALITY, CARD_SIZES),
}


def _blocks(context) -> dict:
    return context.get("site_blocks") or {}


def _get_block(page: str, key: str, site_blocks=None) -> SiteBlock | None:
    cache_key = f"{page}.{key}"
    if site_blocks is not None:
        return site_blocks.get(cache_key)
    return SiteBlock.objects.filter(page=page, key=key).first()


def get_block_text(page: str, key: str, site_blocks=None, fallback: str | None = None) -> str:
    block = _get_block(page, key, site_blocks=site_blocks)
    if block and block.text_html != "":
        text = block.text_html
    elif fallback is not None:
        text = fallback
    else:
        text = BLOCK_DEFAULTS.get((page, key), "")
    if page == "privacy" and key == "privacy_body":
        from landing.privacy_text import ensure_privacy_html

        return ensure_privacy_html(text)
    return text


def is_section_visible(page, visibility_key, site_blocks=None) -> bool:
    value = get_block_text(page, visibility_key, site_blocks=site_blocks, fallback="1")
    return value not in {"0", "false", "False", ""}


@register.simple_tag(takes_context=True)
def block_plain(context, page: str, key: str, fallback: str = "") -> str:
    text = get_block_text(page, key, site_blocks=_blocks(context), fallback=fallback)
    return escape(text)


@register.simple_tag(takes_context=True)
def block_html(context, page: str, key: str, fallback: str = ""):
    text = get_block_text(page, key, site_blocks=_blocks(context), fallback=fallback)
    return mark_safe(text)


@register.simple_tag(takes_context=True)
def section_visible(context, page: str, key: str) -> bool:
    return is_section_visible(page, key, site_blocks=_blocks(context))


@register.simple_tag(takes_context=True)
def block_image_src(context, page: str, key: str, fallback_static: str = "", fallback_url: str = "") -> str:
    block = _get_block(page, key, site_blocks=_blocks(context))
    if block and block.image:
        return block.image.url
    if fallback_url:
        return fallback_url
    if fallback_static:
        return staticfiles_storage.url(fallback_static)
    return ""


@register.filter
def media_or_static(item, static_attr: str = "image_static"):
    image = getattr(item, "image", None)
    if image:
        return image.url
    static_path = getattr(item, static_attr, "") or ""
    if static_path:
        webp = static_webp_candidate(static_path)
        if webp:
            try:
                if staticfiles_storage.exists(webp):
                    return staticfiles_storage.url(webp)
            except Exception:
                pass
        return staticfiles_storage.url(static_path)
    url = getattr(item, "image_url", "") or getattr(item, "src", "") or ""
    return url


@register.filter
def img_src(url, preset: str = "hero") -> str:
    widths, default_w, quality_map, _sizes = _PRESET.get(preset, _PRESET["hero"])
    return responsive_src(
        url or "",
        default_w=default_w,
        quality=quality_map.get(default_w),
    )


@register.filter
def img_srcset(url, preset: str = "hero") -> str:
    widths, _default_w, quality_map, _sizes = _PRESET.get(preset, _PRESET["hero"])
    return responsive_srcset(url or "", widths=widths, quality_map=quality_map)


@register.filter
def img_sizes(preset: str = "hero") -> str:
    return _PRESET.get(preset, _PRESET["hero"])[3]
