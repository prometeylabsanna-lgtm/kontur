from __future__ import annotations

from django import template
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

from landing.block_defaults import BLOCK_DEFAULTS
from landing.models import SiteBlock

register = template.Library()


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


@register.simple_tag(takes_context=True)
def block_image(context, page: str, key: str, css_class: str = "", alt: str = "", fallback_static: str = "", fallback_url: str = "", width: str = "", height: str = "", loading: str = "lazy"):
    src = block_image_src(
        context, page, key, fallback_static=fallback_static, fallback_url=fallback_url
    )
    if not src:
        return ""
    attrs = [f'src="{escape(src)}"', f'alt="{escape(alt)}"']
    if css_class:
        attrs.append(f'class="{escape(css_class)}"')
    if width:
        attrs.append(f'width="{escape(width)}"')
    if height:
        attrs.append(f'height="{escape(height)}"')
    if loading:
        attrs.append(f'loading="{escape(loading)}"')
    attrs.append('decoding="async"')
    return mark_safe(f"<img {' '.join(attrs)} />")


@register.filter
def media_or_static(item, static_attr: str = "image_static"):
    image = getattr(item, "image", None)
    if image:
        return image.url
    static_path = getattr(item, static_attr, "") or ""
    if static_path:
        return staticfiles_storage.url(static_path)
    url = getattr(item, "image_url", "") or getattr(item, "src", "") or ""
    return url
