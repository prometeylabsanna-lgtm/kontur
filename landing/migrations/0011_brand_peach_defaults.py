from django.db import migrations, models

_LEGACY_TO_NEW = {
    "color_button": ({"#b1a091", "#dff250"}, "#f2cfaa"),
    "color_button_hover": ({"#b0a091", "#eaff6b"}, "#e8c49a"),
    "color_fill": ({"#b0a091", "#dff250"}, "#f2cfaa"),
    "color_accent_icon": ({"#b19d91", "#a8bc22"}, "#f2cfaa"),
    "color_accent_text": ({"#806252", "#7e8f1c", "#5f6e12"}, "#907b66"),
}


def forwards_update_brand_colors(apps, schema_editor):
    SiteSettings = apps.get_model("landing", "SiteSettings")
    for obj in SiteSettings.objects.all():
        updates = {}
        for field, (legacy, new) in _LEGACY_TO_NEW.items():
            current = (getattr(obj, field, None) or "").strip().lower()
            if not current or current in legacy:
                if current != new:
                    updates[field] = new
        if updates:
            for key, value in updates.items():
                setattr(obj, key, value)
            obj.save(update_fields=list(updates.keys()))


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("landing", "0010_color_favicon"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="color_accent_icon",
            field=models.CharField(
                default="#f2cfaa",
                help_text="Крапки, лапки, іконки футера",
                max_length=7,
                verbose_name="Акцент · іконки",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="color_accent_text",
            field=models.CharField(
                default="#907b66",
                help_text="Ціни в активному пакеті, посилання, темний акцент тексту",
                max_length=7,
                verbose_name="Акцент · текст",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="color_button",
            field=models.CharField(
                default="#f2cfaa",
                help_text="Заливка акцентних кнопок (формат #RRGGBB)",
                max_length=7,
                verbose_name="Колір кнопки",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="color_button_hover",
            field=models.CharField(
                default="#e8c49a",
                help_text="Колір кнопки при наведенні",
                max_length=7,
                verbose_name="Кнопка · hover",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="color_fill",
            field=models.CharField(
                default="#f2cfaa",
                help_text="Заливка карток і акцентних блоків",
                max_length=7,
                verbose_name="Заливка блоків",
            ),
        ),
        migrations.RunPython(forwards_update_brand_colors, noop_reverse),
    ]
