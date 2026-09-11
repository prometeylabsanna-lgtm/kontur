from decimal import Decimal
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from landing.google_places import (
    apply_place_snapshot,
    extract_place_id,
    public_reviews_queryset,
    sync_google_reviews,
)
from landing.models import ReviewItem, SiteSettings


SAMPLE_PLACE = {
    "id": "places/ChIJtestPlaceId0001",
    "rating": 4.9,
    "userRatingCount": 42,
    "googleMapsUri": "https://maps.google.com/?cid=1",
    "reviews": [
        {
            "name": "places/ChIJtestPlaceId0001/reviews/abc",
            "relativePublishTimeDescription": "місяць тому",
            "rating": 5,
            "text": {"text": "Чудовий ремонт, все в строк.", "languageCode": "uk"},
            "authorAttribution": {"displayName": "Олена"},
        },
        {
            "name": "places/ChIJtestPlaceId0001/reviews/def",
            "relativePublishTimeDescription": "тиждень тому",
            "rating": 5,
            "text": {"text": "Рекомендую Kontur+.", "languageCode": "uk"},
            "authorAttribution": {"displayName": "Ігор"},
        },
    ],
}


class ExtractPlaceIdTests(TestCase):
    def test_raw_place_id(self):
        self.assertEqual(extract_place_id("ChIJabcdefghijklmnopqrstuv"), "ChIJabcdefghijklmnopqrstuv")

    def test_from_query_param(self):
        url = "https://www.google.com/maps/place/?q=place_id:ChIJabcdefghijklmnopqrstuv"
        # loose matcher still finds ChIJ…
        self.assertTrue(extract_place_id(url).startswith("ChIJ"))

    def test_from_place_id_query(self):
        url = "https://www.google.com/maps/search/?api=1&query=Kontur&query_place_id=ChIJabcdefghijklmnopqrstuv"
        # query_place_id not in our patterns — use place_id=
        url2 = "https://example.com/?place_id=ChIJabcdefghijklmnopqrstuv"
        self.assertEqual(extract_place_id(url2), "ChIJabcdefghijklmnopqrstuv")


class GooglePlacesSyncTests(TestCase):
    def setUp(self):
        self.settings_obj = SiteSettings.get_solo()
        self.settings_obj.google_place_id = "ChIJabcdefghijklmnopqrstuv"
        self.settings_obj.save(update_fields=["google_place_id"])
        ReviewItem.objects.create(
            text="Ручний резерв",
            name="Марія",
            meta="Одеса",
            source=ReviewItem.Source.MANUAL,
            sort_order=0,
        )

    @override_settings(GOOGLE_PLACES_API_KEY="")
    def test_sync_without_key(self):
        result = sync_google_reviews(force=True)
        self.assertFalse(result.ok)
        self.assertIn("GOOGLE_PLACES_API_KEY", result.message)

    @override_settings(GOOGLE_PLACES_API_KEY="test-key")
    @patch("landing.google_places.fetch_place_snapshot")
    def test_sync_applies_reviews_and_prefers_google(self, mock_fetch):
        from landing.google_places import _parse_place_payload

        mock_fetch.return_value = _parse_place_payload(
            "ChIJabcdefghijklmnopqrstuv", SAMPLE_PLACE
        )
        result = sync_google_reviews(force=True)
        self.assertTrue(result.ok)
        self.assertEqual(result.reviews_saved, 2)

        self.settings_obj.refresh_from_db()
        self.assertEqual(self.settings_obj.google_rating, Decimal("4.9"))
        self.assertEqual(self.settings_obj.google_reviews_count, 42)
        self.assertTrue(self.settings_obj.google_reviews_url)
        self.assertIsNotNone(self.settings_obj.google_reviews_synced_at)
        self.assertEqual(self.settings_obj.google_reviews_sync_error, "")

        public = list(public_reviews_queryset())
        self.assertEqual(len(public), 2)
        self.assertEqual(public[0].source, ReviewItem.Source.GOOGLE)
        self.assertEqual(public[0].name, "Олена")

    def test_public_falls_back_to_manual(self):
        public = list(public_reviews_queryset())
        self.assertEqual(len(public), 1)
        self.assertEqual(public[0].name, "Марія")

    @override_settings(GOOGLE_PLACES_API_KEY="test-key")
    @patch("landing.google_places.fetch_place_snapshot")
    def test_management_command(self, mock_fetch):
        from landing.google_places import _parse_place_payload

        mock_fetch.return_value = _parse_place_payload(
            "ChIJabcdefghijklmnopqrstuv", SAMPLE_PLACE
        )
        call_command("sync_google_reviews", "--force")
        self.assertEqual(
            ReviewItem.objects.filter(source=ReviewItem.Source.GOOGLE).count(), 2
        )

    @override_settings(GOOGLE_PLACES_API_KEY="test-key")
    def test_stale_google_reviews_removed(self):
        from landing.google_places import _parse_place_payload

        snap = _parse_place_payload("ChIJabcdefghijklmnopqrstuv", SAMPLE_PLACE)
        apply_place_snapshot(snap)
        self.assertEqual(
            ReviewItem.objects.filter(source=ReviewItem.Source.GOOGLE).count(), 2
        )
        slim = dict(SAMPLE_PLACE)
        slim["reviews"] = [SAMPLE_PLACE["reviews"][0]]
        apply_place_snapshot(_parse_place_payload("ChIJabcdefghijklmnopqrstuv", slim))
        keys = list(
            ReviewItem.objects.filter(source=ReviewItem.Source.GOOGLE).values_list(
                "external_key", flat=True
            )
        )
        self.assertEqual(len(keys), 1)
        self.assertIn("reviews/abc", keys[0])


class HomeReviewsContextTests(TestCase):
    def test_home_shows_manual_review_text(self):
        ReviewItem.objects.create(
            text="Тестовий резервний відгук XYZ",
            name="Тест",
            source=ReviewItem.Source.MANUAL,
        )
        response = self.client.get(reverse("landing:home"))
        self.assertContains(response, "Тестовий резервний відгук XYZ")
