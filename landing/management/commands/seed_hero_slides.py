from django.core.management.base import BaseCommand

from landing.hero_slides import ensure_default_hero_slides


class Command(BaseCommand):
    help = "Ідемпотентний seed HeroSlide (створює або лагодить example.com)"

    def handle(self, *args, **options):
        changed = ensure_default_hero_slides(repair_placeholders=True)
        self.stdout.write(self.style.SUCCESS(f"Hero slides created/repaired: {changed}"))
