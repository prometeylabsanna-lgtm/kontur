"""Побудова src/srcset для Unsplash і інших URL з параметрами w/q."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# Hero / full-bleed
HERO_WIDTHS = (640, 960, 1280, 1600)
HERO_DEFAULT_W = 1280
HERO_SIZES = "100vw"
HERO_QUALITY = {
    640: 72,
    960: 76,
    1280: 80,
    1600: 82,
}

# Секційні фото (packages bg тощо)
SECTION_WIDTHS = (640, 960, 1280, 1600)
SECTION_DEFAULT_W = 1280
SECTION_SIZES = "100vw"
SECTION_QUALITY = {
    640: 70,
    960: 74,
    1280: 78,
    1600: 80,
}

# Картки / сітки
CARD_WIDTHS = (400, 640, 900)
CARD_DEFAULT_W = 640
CARD_SIZES = "(max-width: 720px) 85vw, 420px"
CARD_QUALITY = {
    400: 70,
    640: 74,
    900: 78,
}

_UNSPLASH_HOSTS = ("images.unsplash.com", "plus.unsplash.com")


def is_unsplash_url(url: str) -> bool:
    if not url:
        return False
    try:
        host = urlsplit(url).hostname or ""
    except ValueError:
        return False
    host = host.lower().rstrip(".")
    return any(host == h or host.endswith("." + h) for h in _UNSPLASH_HOSTS)


def _with_params(url: str, *, width: int, quality: int) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["auto"] = query.get("auto") or "format"
    query["fit"] = query.get("fit") or "crop"
    query["w"] = str(width)
    query["q"] = str(quality)
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
    )


def responsive_src(
    url: str,
    *,
    default_w: int = HERO_DEFAULT_W,
    quality: int | None = None,
) -> str:
    """Базовий src (менший за w=2000) для Unsplash; інші URL без змін."""
    if not url or not is_unsplash_url(url):
        return url or ""
    q = quality if quality is not None else HERO_QUALITY.get(default_w, 80)
    return _with_params(url, width=default_w, quality=q)


def responsive_srcset(
    url: str,
    *,
    widths: tuple[int, ...] = HERO_WIDTHS,
    quality_map: dict[int, int] | None = None,
) -> str:
    """`640w, 960w, …` для Unsplash; порожній рядок якщо не Unsplash."""
    if not url or not is_unsplash_url(url):
        return ""
    qmap = quality_map or HERO_QUALITY
    parts = []
    for w in widths:
        q = qmap.get(w, 78)
        parts.append(f"{_with_params(url, width=w, quality=q)} {w}w")
    return ", ".join(parts)


def static_webp_candidate(static_path: str) -> str:
    """img/foo.jpg → img/foo.webp (лише рядок шляху)."""
    low = (static_path or "").lower()
    for ext in (".jpg", ".jpeg", ".png"):
        if low.endswith(ext):
            return static_path[: -len(ext)] + ".webp"
    return ""
