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


def ensure_default_hero_slides() -> int:
    if HeroSlide.objects.exists():
        return 0
    created = 0
    for item in DEFAULT_HERO_SLIDES:
        HeroSlide.objects.create(**item, is_active=True)
        created += 1
    return created


def get_hero_slides() -> list[dict]:
    rows = list(
        HeroSlide.objects.filter(is_active=True).order_by("sort_order", "pk")
    )
    slides = []
    for row in rows:
        src = row.src
        if not src:
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
