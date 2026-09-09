from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import ImageField

from landing.image_webp import convert_instance_images, is_webp_name


class Command(BaseCommand):
    help = "Конвертує всі наявні ImageField (landing) у WebP і видаляє оригінали."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Лише показати, що буде конвертовано, без запису.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        converted = 0
        skipped = 0
        errors = 0

        for model in apps.get_app_config("landing").get_models():
            if model._meta.proxy:
                continue
            image_fields = [
                f.name for f in model._meta.get_fields() if isinstance(f, ImageField)
            ]
            if not image_fields:
                continue

            for obj in model.objects.all().iterator():
                pending = []
                for field_name in image_fields:
                    field_file = getattr(obj, field_name, None)
                    if not field_file or not field_file.name:
                        skipped += 1
                        continue
                    if is_webp_name(field_file.name):
                        skipped += 1
                        continue
                    pending.append(field_name)

                if not pending:
                    continue

                label = (
                    f"{model.__name__}#{obj.pk} "
                    + ", ".join(
                        f"{fn}={getattr(obj, fn).name}" for fn in pending
                    )
                )
                if dry_run:
                    self.stdout.write(f"[dry-run] {label}")
                    converted += len(pending)
                    continue

                try:
                    changed = convert_instance_images(obj, force=True)
                    if not changed:
                        errors += 1
                        self.stderr.write(self.style.ERROR(f"FAIL {label}"))
                        continue
                    obj.save(update_fields=changed)
                    converted += len(changed)
                    self.stdout.write(self.style.SUCCESS(f"OK {label}"))
                except Exception as exc:
                    errors += 1
                    self.stderr.write(self.style.ERROR(f"FAIL {label}: {exc}"))

        self.stdout.write(
            self.style.NOTICE(
                f"Готово: converted={converted}, skipped={skipped}, errors={errors}"
                + (" (dry-run)" if dry_run else "")
            )
        )
