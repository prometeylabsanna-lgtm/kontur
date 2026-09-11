# Generated manually for color_favicon

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("landing", "0009_google_places_reviews"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="color_favicon",
            field=models.CharField(
                default="#92817c",
                help_text="Колір знака K+ у вкладці браузера (фон лишається чорним)",
                max_length=7,
                verbose_name="Колір фавіконки",
            ),
        ),
    ]
