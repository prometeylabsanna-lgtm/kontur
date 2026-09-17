"""Прев’ю зображень у CMS formsets (файл / static / URL)."""

from __future__ import annotations

from typing import Any


def cms_preview_url_for(instance: Any) -> str:
    """URL для маленького прев’ю в адмінці."""
    if instance is None:
        return ""

    image = getattr(instance, "image", None)
    if image:
        try:
            name = getattr(image, "name", "") or ""
            if name:
                return image.url
        except (ValueError, OSError):
            pass

    from landing.responsive_images import (
        CARD_DEFAULT_W,
        CARD_WIDTHS,
        HERO_DEFAULT_W,
        HERO_WIDTHS,
        responsive_src,
        static_path_stem,
        static_responsive_src,
        static_webp_candidate,
    )
    from django.contrib.staticfiles import finders
    from django.contrib.staticfiles.storage import staticfiles_storage

    model_name = instance.__class__.__name__
    if model_name == "HeroSlide":
        default_w, widths = HERO_DEFAULT_W, HERO_WIDTHS
    else:
        default_w, widths = CARD_DEFAULT_W, CARD_WIDTHS

    image_url = (getattr(instance, "image_url", "") or "").strip()
    if image_url:
        return responsive_src(image_url, default_w=default_w, widths=widths)

    static_path = (getattr(instance, "image_static", "") or "").strip()
    if static_path:
        stem = static_path_stem(static_path)
        if stem:
            local = static_responsive_src(stem, default_w=default_w, widths=widths)
            if local:
                return local
        webp = static_webp_candidate(static_path)
        if webp and finders.find(webp):
            return staticfiles_storage.url(webp)
        if finders.find(static_path):
            return staticfiles_storage.url(static_path)

    return ""


def cms_preview_caption_for(instance: Any, preview_url: str) -> str:
    if not preview_url:
        return ""
    image = getattr(instance, "image", None)
    if image and getattr(image, "name", ""):
        return ""
    if (getattr(instance, "image_url", "") or "").strip():
        return "Поточне фото з посилання"
    if (getattr(instance, "image_static", "") or "").strip():
        return "Поточне фото зі static"
    return "Поточне фото"
