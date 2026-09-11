from django.test import TestCase
from django.urls import reverse

from landing.responsive_images import (
    is_unsplash_url,
    responsive_src,
    responsive_srcset,
    static_webp_candidate,
)

CREDIT_URL = "https://www.prometeylabs.com/corporate-website-v2/"


class ResponsiveImagesTests(TestCase):
    def test_unsplash_src_reduces_width(self):
        url = (
            "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0"
            "?auto=format&fit=crop&w=2000&q=90"
        )
        out = responsive_src(url, default_w=1280, quality=80)
        self.assertIn("w=1280", out)
        self.assertIn("q=80", out)
        self.assertNotIn("w=2000", out)

    def test_srcset_has_multiple_widths(self):
        url = (
            "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0"
            "?auto=format&fit=crop&w=2000&q=90"
        )
        srcset = responsive_srcset(url)
        self.assertIn("640w", srcset)
        self.assertIn("1280w", srcset)
        self.assertTrue(is_unsplash_url(url))

    def test_non_unsplash_passthrough(self):
        url = "/media/hero/photo.webp"
        self.assertEqual(responsive_src(url), url)
        self.assertEqual(responsive_srcset(url), "")

    def test_webp_candidate(self):
        self.assertEqual(
            static_webp_candidate("img/advantages/adv-odesa.jpg"),
            "img/advantages/adv-odesa.webp",
        )


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


class HomePerfMarkupTests(TestCase):
    def test_home_has_lcp_preload_and_deferred_css(self):
        response = self.client.get(reverse("landing:home"))
        self.assertContains(response, 'rel="preload"')
        self.assertContains(response, 'as="image"')
        self.assertContains(response, 'aria-labelledby="areaLabel"')
        self.assertContains(response, 'role="group"')
        self.assertContains(
            response, 'class="sr-only">Переваги Kontur+</h2>', html=False
        )
        self.assertContains(response, "media=\"print\" onload=\"this.media='all'\"")

    def test_home_hero_uses_srcset_when_unsplash(self):
        response = self.client.get(reverse("landing:home"))
        content = response.content.decode("utf-8")
        if "images.unsplash.com" in content:
            self.assertIn("srcset=", content)
            self.assertIn("640w", content)


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


class FaviconColorTests(TestCase):
    def test_home_links_dynamic_favicon(self):
        from landing.models import SiteSettings

        settings_obj = SiteSettings.get_solo()
        settings_obj.color_favicon = "#c4a484"
        settings_obj.save(update_fields=["color_favicon"])

        response = self.client.get(reverse("landing:home"))
        self.assertContains(response, "/favicon-32.png?v=c4a484")
        self.assertContains(response, "/favicon.ico?v=c4a484")

    def test_favicon_png_is_colored_png(self):
        from landing.models import SiteSettings

        settings_obj = SiteSettings.get_solo()
        settings_obj.color_favicon = "#aabbcc"
        settings_obj.save(update_fields=["color_favicon"])

        response = self.client.get(reverse("landing:favicon_png", kwargs={"size": 32}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertTrue(response.content.startswith(b"\x89PNG"))

    def test_favicon_ico_ok(self):
        response = self.client.get(reverse("landing:favicon_ico"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("image/", response["Content-Type"])
        self.assertGreater(len(response.content), 64)
