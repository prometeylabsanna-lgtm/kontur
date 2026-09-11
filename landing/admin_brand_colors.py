from __future__ import annotations

from django import forms
from django.contrib import admin

from unfold.admin import ModelAdmin

from .admin_site_content_proxies import (
    ReadableUnfoldFieldsMixin,
    SingletonModelAdminMixin,
)
from .brand_colors import (
    DEFAULT_COLOR_BUTTON,
    DEFAULT_COLOR_BUTTON_HOVER,
    DEFAULT_COLOR_BUTTON_TEXT,
    DEFAULT_COLOR_FILL,
    HEX_COLOR_RE,
)
from .models_proxies import BrandColorSettings


class HexColorInput(forms.TextInput):
    input_type = "color"
    template_name = "admin/landing/widgets/cms_color_input.html"

    def __init__(self, attrs=None):
        base = {
            "class": "cms-color-input__picker",
        }
        if attrs:
            base.update(attrs)
        super().__init__(attrs=base)


class BrandColorForm(forms.ModelForm):
    class Meta:
        model = BrandColorSettings
        fields = (
            "color_button",
            "color_button_text",
            "color_button_hover",
            "color_fill",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        defaults = {
            "color_button": DEFAULT_COLOR_BUTTON,
            "color_button_text": DEFAULT_COLOR_BUTTON_TEXT,
            "color_button_hover": DEFAULT_COLOR_BUTTON_HOVER,
            "color_fill": DEFAULT_COLOR_FILL,
        }
        for name, fallback in defaults.items():
            field = self.fields[name]
            field.widget = HexColorInput()
            value = self.initial.get(name) or getattr(self.instance, name, None)
            if not value:
                self.initial[name] = fallback

    def clean_color_button(self):
        return self._clean_hex("color_button", DEFAULT_COLOR_BUTTON)

    def clean_color_button_text(self):
        return self._clean_hex("color_button_text", DEFAULT_COLOR_BUTTON_TEXT)

    def clean_color_button_hover(self):
        return self._clean_hex("color_button_hover", DEFAULT_COLOR_BUTTON_HOVER)

    def clean_color_fill(self):
        return self._clean_hex("color_fill", DEFAULT_COLOR_FILL)

    def _clean_hex(self, field_name: str, fallback: str) -> str:
        value = (self.cleaned_data.get(field_name) or "").strip()
        if not HEX_COLOR_RE.match(value):
            raise forms.ValidationError("Вкажіть колір у форматі #RRGGBB.")
        return value.lower()


@admin.register(BrandColorSettings)
class BrandColorSettingsAdmin(
    ReadableUnfoldFieldsMixin, SingletonModelAdminMixin, ModelAdmin
):
    form = BrandColorForm
    fieldsets = (
        (
            "Акцентні кнопки",
            {
                "description": "Кольори всіх btn--primary / btn--light та іконки дзвінка.",
                "fields": (
                    "color_button",
                    "color_button_text",
                    "color_button_hover",
                ),
            },
        ),
        (
            "Заливка блоків",
            {
                "description": "Салатові картки (рекомендований пакет тощо) і акценти заливки.",
                "fields": ("color_fill",),
            },
        ),
    )

    class Media:
        css = {"all": ("css/admin/brand_colors.css",)}
        js = ("js/admin/brand_colors.js",)
