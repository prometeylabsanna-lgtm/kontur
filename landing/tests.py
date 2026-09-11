from django.test import TestCase
from django.urls import reverse

CREDIT_URL = "https://www.prometeylabs.com/corporate-website-v2/"


class FooterDeveloperLinkTests(TestCase):
    def test_home_has_nofollow_credit_link(self):
        response = self.client.get(reverse("landing:home"))
        self.assertContains(response, CREDIT_URL)
        self.assertContains(response, "nofollow")
        self.assertContains(response, ">PrometeyLabs</a>")
        self.assertContains(response, "site-footer__credit-link")

    def test_privacy_shows_credit_without_link(self):
        response = self.client.get(reverse("landing:privacy"))
        self.assertContains(response, "PrometeyLabs")
        self.assertNotContains(response, CREDIT_URL)
        self.assertNotContains(response, "site-footer__credit-link")


class CookieConsentTests(TestCase):
    def test_home_includes_cookie_consent_banner(self):
        response = self.client.get(reverse("landing:home"))
        self.assertContains(response, 'id="cookie-consent"')
        self.assertContains(response, 'data-cookie-choice="necessary"')
        self.assertContains(response, 'data-cookie-choice="all"')
        self.assertContains(response, "cookie-consent.js")

    def test_privacy_includes_cookie_consent_banner(self):
        response = self.client.get(reverse("landing:privacy"))
        self.assertContains(response, 'id="cookie-consent"')


class PrivacyLayoutTests(TestCase):
    def test_privacy_body_renders_headings_from_plain_text(self):
        from django.core.cache import cache

        from landing.context_processors import SITE_BLOCKS_CACHE_KEY
        from landing.models import SiteBlock

        SiteBlock.objects.update_or_create(
            page="privacy",
            key="privacy_body",
            defaults={
                "label": "Текст сторінки",
                "content_type": "text",
                "text_html": (
                    "Вступний абзац.\n\n"
                    "1. Оператор даних\n"
                    "Kontur+ в Одесі.\n\n"
                    "2. Які дані ми збираємо\n"
                    "Ім’я та телефон."
                ),
            },
        )
        cache.delete(SITE_BLOCKS_CACHE_KEY)
        response = self.client.get(reverse("landing:privacy"))
        self.assertContains(response, "<h2>1. Оператор даних</h2>", html=False)
        self.assertContains(response, "<h2>2. Які дані ми збираємо</h2>", html=False)
        self.assertContains(response, "<p>Kontur+ в Одесі.</p>", html=False)


class AdminUrlHardeningTests(TestCase):
    def test_legacy_admin_paths_return_400(self):
        for path in ("/admin", "/admin/", "/admin/login/"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 400, path)
            self.assertContains(response, "Некоректний запит", status_code=400)
            self.assertNotContains(response, "kontur-plus-cms", status_code=400)

    def test_custom_cms_url_is_reachable(self):
        response = self.client.get("/kontur-plus-cms/")
        self.assertIn(response.status_code, (200, 302))
