from __future__ import annotations

from .models import HeroSlide

DEFAULT_HERO_SLIDES = (
    {
        "image_url": (
            "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0"
            "?auto=format&fit=crop&w=2000&q=90"
        ),
        "alt_text": "Інтер’єр після ремонту",
        "sort_order": 0,
    },
    {
        "image_url": (
            "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c"
            "?auto=format&fit=crop&w=2000&q=90"
        ),
        "alt_text": "Сучасна вітальня",
        "sort_order": 1,
    },
    {
        "image_url": (
            "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace"
            "?auto=format&fit=crop&w=2000&q=90"
        ),
        "alt_text": "Кухня під ключ",
        "sort_order": 2,
    },
)

_PLACEHOLDER_HOSTS = ("example.com", "example.org", "example.net")


def _is_placeholder_url(url: str) -> bool:
    low = (url or "").strip().lower()
    if not low:
        return True
    return any(host in low for host in _PLACEHOLDER_HOSTS)


def ensure_default_hero_slides(*, repair_placeholders: bool = True) -> int:
    """Create defaults if empty; optionally replace example.com placeholders."""
    if not HeroSlide.objects.exists():
        created = 0
        for item in DEFAULT_HERO_SLIDES:
            HeroSlide.objects.create(**item, is_active=True)
            created += 1
        return created

    if not repair_placeholders:
        return 0

    repaired = 0
    rows = list(HeroSlide.objects.all().order_by("sort_order", "pk"))
    for idx, row in enumerate(rows):
        has_file = bool(row.image)
        if has_file or not _is_placeholder_url(row.image_url):
            continue
        defaults = DEFAULT_HERO_SLIDES[min(idx, len(DEFAULT_HERO_SLIDES) - 1)]
        row.image_url = defaults["image_url"]
        if not (row.alt_text or "").strip() or len(row.alt_text.strip()) <= 2:
            row.alt_text = defaults["alt_text"]
        row.is_active = True
        row.save(update_fields=["image_url", "alt_text", "is_active"])
        repaired += 1
    return repaired


def get_hero_slides() -> list[dict]:
    rows = list(
        HeroSlide.objects.filter(is_active=True).order_by("sort_order", "pk")
    )
    slides = []
    for row in rows:
        src = row.src
        if not src or _is_placeholder_url(src):
            continue
        slides.append(
            {
                "src": src,
                "alt": row.alt_text or "",
                "pk": row.pk,
            }
        )
    if slides:
        return slides
    return [
        {
            "src": item["image_url"],
            "alt": item["alt_text"],
            "pk": None,
        }
        for item in DEFAULT_HERO_SLIDES
    ]
