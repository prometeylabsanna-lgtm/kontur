"""Google Places API (New) — рейтинг і відгуки для блоку #proof."""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

from django.conf import settings
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

PLACES_DETAILS_URL = "https://places.googleapis.com/v1/places/{place_id}"
FIELD_MASK = "id,rating,userRatingCount,googleMapsUri,reviews"
REQUEST_TIMEOUT_SEC = 12

_PLACE_ID_RE = re.compile(r"^ChIJ[\w-]+$")
_PLACE_ID_QUERY_RE = re.compile(
    r"[?&](?:place_id|query_place_id)=(ChIJ[\w-]+)", re.I
)
_PLACE_ID_PATH_RE = re.compile(r"places/(ChIJ[\w-]+)", re.I)
_PLACE_ID_LOOSE_RE = re.compile(r"(ChIJ[\w-]{10,})")


@dataclass
class GoogleReviewPayload:
    external_key: str
    name: str
    text: str
    meta: str
    rating: float | None = None


@dataclass
class PlaceSnapshot:
    place_id: str
    rating: Decimal | None = None
    reviews_count: int | None = None
    maps_url: str = ""
    reviews: list[GoogleReviewPayload] = field(default_factory=list)


@dataclass
class SyncResult:
    ok: bool
    message: str
    rating: Decimal | None = None
    reviews_count: int | None = None
    reviews_saved: int = 0


def get_api_key() -> str:
    return (getattr(settings, "GOOGLE_PLACES_API_KEY", "") or "").strip()


def is_configured() -> bool:
    return bool(get_api_key())


def extract_place_id(value: str) -> str:
    """Приймає Place ID або URL Maps / Places і повертає ChIJ… або ''."""
    raw = (value or "").strip()
    if not raw:
        return ""
    if _PLACE_ID_RE.match(raw):
        return raw
    for pattern in (_PLACE_ID_QUERY_RE, _PLACE_ID_PATH_RE, _PLACE_ID_LOOSE_RE):
        match = pattern.search(raw)
        if match:
            return match.group(1)
    return ""


def resolve_place_id(site_settings=None) -> str:
    from .models import SiteSettings

    obj = site_settings or SiteSettings.get_solo()
    from_db = extract_place_id(obj.google_place_id or "")
    if from_db:
        return from_db
    env_id = (getattr(settings, "GOOGLE_PLACE_ID", "") or "").strip()
    return extract_place_id(env_id)


def fetch_place_snapshot(place_id: str, *, api_key: str | None = None) -> PlaceSnapshot:
    key = (api_key or get_api_key()).strip()
    if not key:
        raise ValueError("Не задано GOOGLE_PLACES_API_KEY у .env")
    pid = extract_place_id(place_id) or place_id.strip()
    if not pid:
        raise ValueError("Некоректний Place ID")

    url = PLACES_DETAILS_URL.format(place_id=urllib.parse.quote(pid, safe=""))
    url = f"{url}?languageCode=uk"
    request = urllib.request.Request(
        url,
        headers={
            "X-Goog-Api-Key": key,
            "X-Goog-FieldMask": FIELD_MASK,
            "Accept": "application/json",
            "User-Agent": "KonturPlus/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SEC) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode("utf-8", errors="replace")[:400]
        except Exception:  # pragma: no cover
            body = ""
        raise RuntimeError(f"Places API HTTP {exc.code}: {body or exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Мережева помилка Places API: {exc.reason}") from exc

    return _parse_place_payload(pid, payload)


def _parse_place_payload(place_id: str, payload: dict[str, Any]) -> PlaceSnapshot:
    rating = None
    raw_rating = payload.get("rating")
    if raw_rating is not None:
        try:
            rating = Decimal(str(raw_rating)).quantize(Decimal("0.1"))
        except (InvalidOperation, ValueError):
            rating = None

    count = payload.get("userRatingCount")
    reviews_count = int(count) if count is not None else None
    maps_url = (payload.get("googleMapsUri") or "").strip()

    reviews: list[GoogleReviewPayload] = []
    for item in payload.get("reviews") or []:
        parsed = _parse_review(item)
        if parsed:
            reviews.append(parsed)

    return PlaceSnapshot(
        place_id=place_id,
        rating=rating,
        reviews_count=reviews_count,
        maps_url=maps_url,
        reviews=reviews,
    )


def _parse_review(item: dict[str, Any]) -> GoogleReviewPayload | None:
    text_obj = item.get("text") or item.get("originalText") or {}
    text = (text_obj.get("text") if isinstance(text_obj, dict) else "") or ""
    text = text.strip()
    if not text:
        return None

    author = item.get("authorAttribution") or {}
    name = (author.get("displayName") or "Клієнт Google").strip()[:80]
    external = (item.get("name") or "").strip()
    if not external:
        external = f"google:{name}:{text[:48]}"

    relative = (item.get("relativePublishTimeDescription") or "").strip()
    rating = item.get("rating")
    meta_parts = ["Google"]
    if rating is not None:
        meta_parts.append(f"{rating}★")
    if relative:
        meta_parts.append(relative)
    meta = " · ".join(meta_parts)[:120]

    return GoogleReviewPayload(
        external_key=external[:255],
        name=name,
        text=text,
        meta=meta,
        rating=float(rating) if rating is not None else None,
    )


@transaction.atomic
def apply_place_snapshot(snapshot: PlaceSnapshot, site_settings=None) -> SyncResult:
    from .models import ReviewItem, SiteSettings

    obj = site_settings or SiteSettings.get_solo()
    update_fields = [
        "google_reviews_synced_at",
        "google_reviews_sync_error",
        "google_place_id",
    ]

    normalized_id = extract_place_id(snapshot.place_id) or snapshot.place_id
    if normalized_id and obj.google_place_id != normalized_id:
        obj.google_place_id = normalized_id

    if snapshot.rating is not None:
        obj.google_rating = snapshot.rating
        update_fields.append("google_rating")
    if snapshot.reviews_count is not None:
        obj.google_reviews_count = snapshot.reviews_count
        update_fields.append("google_reviews_count")
    if snapshot.maps_url:
        obj.google_reviews_url = snapshot.maps_url
        update_fields.append("google_reviews_url")

    kept_keys: list[str] = []
    for idx, review in enumerate(snapshot.reviews):
        kept_keys.append(review.external_key)
        ReviewItem.objects.update_or_create(
            source=ReviewItem.Source.GOOGLE,
            external_key=review.external_key,
            defaults={
                "text": review.text,
                "name": review.name,
                "meta": review.meta,
                "sort_order": idx,
                "is_active": True,
            },
        )

    stale = ReviewItem.objects.filter(source=ReviewItem.Source.GOOGLE)
    if kept_keys:
        stale = stale.exclude(external_key__in=kept_keys)
    stale_count = stale.count()
    stale.delete()

    obj.google_reviews_synced_at = timezone.now()
    obj.google_reviews_sync_error = ""
    obj.save(update_fields=list(dict.fromkeys(update_fields)))

    msg = (
        f"Синхронізовано: рейтинг {obj.google_rating or '—'}, "
        f"відгуків у профілі {obj.google_reviews_count or 0}, "
        f"карток на сайті {len(kept_keys)}"
    )
    if stale_count:
        msg += f" (прибрано застарілих {stale_count})"
    return SyncResult(
        ok=True,
        message=msg,
        rating=obj.google_rating,
        reviews_count=obj.google_reviews_count,
        reviews_saved=len(kept_keys),
    )


def sync_google_reviews(*, force: bool = False) -> SyncResult:
    """Тягне Place Details і оновлює SiteSettings + ReviewItem (source=google)."""
    from .models import SiteSettings

    obj = SiteSettings.get_solo()
    if not force and not obj.google_reviews_auto_sync:
        return SyncResult(ok=False, message="Автосинхронізацію вимкнено в налаштуваннях.")

    if not is_configured():
        msg = "Додайте GOOGLE_PLACES_API_KEY у .env і перезапустіть додаток."
        _store_sync_error(obj, msg)
        return SyncResult(ok=False, message=msg)

    place_id = resolve_place_id(obj)
    if not place_id:
        msg = "Вкажіть Google Place ID (або посилання Maps) у секції «Відгуки та кейси»."
        _store_sync_error(obj, msg)
        return SyncResult(ok=False, message=msg)

    try:
        snapshot = fetch_place_snapshot(place_id)
        return apply_place_snapshot(snapshot, site_settings=obj)
    except Exception as exc:
        msg = str(exc)[:500]
        logger.warning("Google Places sync failed: %s", msg)
        _store_sync_error(obj, msg)
        return SyncResult(ok=False, message=msg)


def _store_sync_error(obj, message: str) -> None:
    obj.google_reviews_sync_error = message[:500]
    obj.save(update_fields=["google_reviews_sync_error"])


def public_reviews_queryset():
    """Google-відгуки, якщо є; інакше ручний резерв."""
    from .models import ReviewItem

    google = ReviewItem.objects.filter(
        is_active=True, source=ReviewItem.Source.GOOGLE
    ).order_by("sort_order", "pk")
    if google.exists():
        return google
    return ReviewItem.objects.filter(
        is_active=True, source=ReviewItem.Source.MANUAL
    ).order_by("sort_order", "pk")
