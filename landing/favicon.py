"""Перефарбування існуючої фавіконки K+ під колір з адмінки."""

from __future__ import annotations

from functools import lru_cache
from io import BytesIO
from pathlib import Path

from django.conf import settings
from PIL import Image

from .brand_colors import DEFAULT_COLOR_FAVICON, normalize_hex

_MASTER = Path(settings.BASE_DIR) / "static" / "img" / "favicon.png"
_ALLOWED_SIZES = frozenset({16, 32, 48, 180, 192})


def resolve_favicon_color(settings_obj=None) -> str:
    if settings_obj is None:
        from .models import SiteSettings

        settings_obj = SiteSettings.get_solo()
    return normalize_hex(
        getattr(settings_obj, "color_favicon", None), DEFAULT_COLOR_FAVICON
    )


def favicon_cache_bust(settings_obj=None) -> str:
    return resolve_favicon_color(settings_obj).lstrip("#")


def _hex_rgb(hex_color: str) -> tuple[int, int, int]:
    raw = hex_color.lstrip("#")
    return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)


def _recolor_image(src: Image.Image, hex_color: str) -> Image.Image:
    """Чорний фон лишаємо; інтенсивність знака → новий RGB (з antialias)."""
    tr, tg, tb = _hex_rgb(hex_color)
    rgba = src.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    for y in range(height):
        for x in range(width):
            pr, pg, pb, pa = pixels[x, y]
            if pa == 0:
                continue
            intensity = (pr + pg + pb) / (3 * 255)
            if intensity < 0.02:
                pixels[x, y] = (0, 0, 0, 255)
                continue
            pixels[x, y] = (
                int(tr * intensity),
                int(tg * intensity),
                int(tb * intensity),
                255,
            )
    return rgba


@lru_cache(maxsize=48)
def render_favicon_png(hex_color: str, size: int) -> bytes:
    color = normalize_hex(hex_color, DEFAULT_COLOR_FAVICON)
    size = size if size in _ALLOWED_SIZES else 32
    master = Image.open(_MASTER)
    colored = _recolor_image(master, color)
    if colored.size != (size, size):
        colored = colored.resize((size, size), Image.Resampling.LANCZOS)
    buf = BytesIO()
    colored.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


@lru_cache(maxsize=16)
def render_favicon_ico(hex_color: str) -> bytes:
    color = normalize_hex(hex_color, DEFAULT_COLOR_FAVICON)
    master = Image.open(_MASTER)
    colored = _recolor_image(master, color)
    sizes = [(16, 16), (32, 32), (48, 48)]
    frames = [colored.resize(sz, Image.Resampling.LANCZOS) for sz in sizes]
    buf = BytesIO()
    frames[0].save(
        buf,
        format="ICO",
        sizes=sizes,
        append_images=frames[1:],
    )
    return buf.getvalue()


def clear_favicon_render_cache() -> None:
    render_favicon_png.cache_clear()
    render_favicon_ico.cache_clear()
