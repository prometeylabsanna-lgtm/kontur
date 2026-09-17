"""Побудова src/srcset для Unsplash, локальних static і інших URL."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# Hero / full-bleed
HERO_WIDTHS = (640, 960, 1280, 1600)
HERO_DEFAULT_W = 960
HERO_SIZES = "100vw"
HERO_QUALITY = {
    640: 72,
    960: 76,
    1280: 80,
    1600: 82,
}

# Секційні фото (packages bg тощо)
SECTION_WIDTHS = (640, 960, 1280, 1600)
SECTION_DEFAULT_W = 960
SECTION_SIZES = "100vw"
SECTION_QUALITY = {
    640: 70,
    960: 74,
    1280: 78,
    1600: 80,
}

# Картки / сітки / advantages
CARD_WIDTHS = (480, 640, 960)
CARD_DEFAULT_W = 640
CARD_SIZES = "(max-width: 720px) 85vw, 420px"
CARD_QUALITY = {
    480: 68,
    640: 72,
    960: 74,
}

_UNSPLASH_HOSTS = ("images.unsplash.com", "plus.unsplash.com")

# Self-hosted copies of previously remote Unsplash assets (stem without width/ext).
UNSPLASH_LOCAL_STEMS: dict[str, str] = {
    "photo-1600210492486-724fe5c67fb0": "img/hero/hero-01",
    "photo-1600607687939-ce8a6c25118c": "img/hero/hero-02",
    "photo-1616486338812-3dadae4b4ace": "img/hero/hero-03",
    "photo-1503387762-592deb58ef4e": "img/design/design-01",
    "photo-1618221195710-dd6b41faaea6": "img/design/design-02",
}


def is_unsplash_url(url: str) -> bool:
    if not url:
        return False
    try:
        host = urlsplit(url).hostname or ""
    except ValueError:
        return False
    host = host.lower().rstrip(".")
    return any(host == h or host.endswith("." + h) for h in _UNSPLASH_HOSTS)


def unsplash_photo_id(url: str) -> str:
    if not url:
        return ""
    try:
        path = urlsplit(url).path or ""
    except ValueError:
        return ""
    name = path.rsplit("/", 1)[-1]
    return name.split("?", 1)[0]


def local_stem_for_url(url: str) -> str:
    """Повертає static stem (`img/hero/hero-01`) або порожній рядок."""
    if not url:
        return ""
    raw = url.strip()
    if raw.startswith("img/"):
        return _strip_width_suffix(_stem_without_ext(raw))
    if "/static/img/" in raw:
        part = raw.split("/static/", 1)[-1]
        return _strip_width_suffix(_stem_without_ext(part))
    if is_unsplash_url(raw):
        return UNSPLASH_LOCAL_STEMS.get(unsplash_photo_id(raw), "")
    return ""


def _stem_without_ext(path: str) -> str:
    low = path.lower()
    for ext in (".webp", ".jpg", ".jpeg", ".png"):
        if low.endswith(ext):
            return path[: -len(ext)]
    return path


def _strip_width_suffix(stem: str) -> str:
    import re

    return re.sub(r"-\d+$", "", stem)


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


def _static_url(path: str) -> str:
    from django.contrib.staticfiles import finders
    from django.contrib.staticfiles.storage import staticfiles_storage

    if not path:
        return ""
    try:
        if finders.find(path):
            return staticfiles_storage.url(path)
    except Exception:
        pass
    try:
        if staticfiles_storage.exists(path):
            return staticfiles_storage.url(path)
    except Exception:
        pass
    return ""


def static_variant_path(stem: str, width: int | None = None, ext: str = ".webp") -> str:
    if width is None:
        return f"{stem}{ext}"
    return f"{stem}-{width}{ext}"


def static_responsive_src(
    stem: str,
    *,
    default_w: int,
    widths: tuple[int, ...] | None = None,
) -> str:
    """URL дефолтного розміру; fallback на stem.webp."""
    candidates = []
    if widths:
        # prefer default_w, then closest available
        ordered = [default_w] + [w for w in widths if w != default_w]
        for w in ordered:
            candidates.append(static_variant_path(stem, w))
    candidates.append(static_variant_path(stem))
    for path in candidates:
        url = _static_url(path)
        if url:
            return url
    return ""


def static_responsive_srcset(stem: str, *, widths: tuple[int, ...]) -> str:
    parts = []
    for w in widths:
        url = _static_url(static_variant_path(stem, w))
        if url:
            parts.append(f"{url} {w}w")
    return ", ".join(parts)


def responsive_src(
    url: str,
    *,
    default_w: int = HERO_DEFAULT_W,
    quality: int | None = None,
    widths: tuple[int, ...] | None = None,
) -> str:
    """Базовий src: local static → Unsplash params → passthrough."""
    if not url:
        return ""
    stem = local_stem_for_url(url)
    if stem:
        local = static_responsive_src(
            stem, default_w=default_w, widths=widths or HERO_WIDTHS
        )
        if local:
            return local
    if is_unsplash_url(url):
        q = quality if quality is not None else HERO_QUALITY.get(default_w, 80)
        return _with_params(url, width=default_w, quality=q)
    if url.startswith("img/"):
        return _static_url(url) or url
    return url


def responsive_srcset(
    url: str,
    *,
    widths: tuple[int, ...] = HERO_WIDTHS,
    quality_map: dict[int, int] | None = None,
) -> str:
    """Srcset для local static або Unsplash; інакше порожній рядок."""
    if not url:
        return ""
    stem = local_stem_for_url(url)
    if stem:
        return static_responsive_srcset(stem, widths=widths)
    if is_unsplash_url(url):
        qmap = quality_map or HERO_QUALITY
        parts = []
        for w in widths:
            q = qmap.get(w, 78)
            parts.append(f"{_with_params(url, width=w, quality=q)} {w}w")
        return ", ".join(parts)
    return ""


def static_webp_candidate(static_path: str) -> str:
    """img/foo.jpg → img/foo.webp (лише рядок шляху)."""
    low = (static_path or "").lower()
    for ext in (".jpg", ".jpeg", ".png"):
        if low.endswith(ext):
            return static_path[: -len(ext)] + ".webp"
    return ""


def static_path_stem(static_path: str) -> str:
    """img/advantages/adv-odesa.webp → img/advantages/adv-odesa."""
    if not static_path:
        return ""
    path = static_webp_candidate(static_path) or static_path
    return _strip_width_suffix(_stem_without_ext(path))
