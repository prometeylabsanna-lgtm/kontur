IMAGE_PROFILES = {
    "hero": {
        "recommended": "1920×1080",
        "max_size_mb": 3,
        "note": "Горизонтальне фото інтер’єру",
    },
    "block_image": {
        "recommended": "1200×800",
        "max_size_mb": 2,
        "note": "Секційне фото",
    },
    "advantage": {
        "recommended": "1200×675",
        "max_size_mb": 2,
        "note": "Картка переваги",
    },
    "case": {
        "recommended": "1200×900",
        "max_size_mb": 2,
        "note": "Кейс",
    },
}

TEXT_LIMITS = {
    "hero_title": 120,
    "hero_lead": 280,
    "packages_title": 100,
    "packages_lead": 220,
}


def get_image_hint(profile: str) -> str:
    data = IMAGE_PROFILES.get(profile) or IMAGE_PROFILES["block_image"]
    return (
        f"Рекомендовано {data['recommended']}, до {data['max_size_mb']} МБ. "
        f"{data.get('note', '')} "
        "Після збереження автоматично конвертується в WebP."
    ).strip()


def get_text_limit_hint(key: str) -> str:
    limit = TEXT_LIMITS.get(key)
    if not limit:
        return ""
    return f"Орієнтовно до {limit} символів."
