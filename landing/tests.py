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
