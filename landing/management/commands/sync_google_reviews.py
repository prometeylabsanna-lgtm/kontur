from django.core.management.base import BaseCommand

from landing.google_places import sync_google_reviews


class Command(BaseCommand):
    help = (
        "Синхронізує рейтинг і відгуки з Google Places API (New). "
        "Потрібні GOOGLE_PLACES_API_KEY і Place ID у CMS або GOOGLE_PLACE_ID."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Синхронізувати навіть якщо автосинхронізацію вимкнено в CMS.",
        )

    def handle(self, *args, **options):
        result = sync_google_reviews(force=bool(options.get("force")))
        if result.ok:
            self.stdout.write(self.style.SUCCESS(result.message))
        else:
            self.stderr.write(self.style.ERROR(result.message))
            raise SystemExit(1)
