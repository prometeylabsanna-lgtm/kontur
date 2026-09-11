from __future__ import annotations

from django import forms
from django.contrib import admin

from unfold.admin import ModelAdmin

from .admin_site_content_proxies import (
    ReadableUnfoldFieldsMixin,
    SingletonModelAdminMixin,
)
from .brand_colors import (
    DEFAULT_COLOR_ACCENT_ICON,
    DEFAULT_COLOR_ACCENT_TEXT,
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


_COLOR_DEFAULTS = {
    "color_button": DEFAULT_COLOR_BUTTON,
    "color_button_text": DEFAULT_COLOR_BUTTON_TEXT,
    "color_button_hover": DEFAULT_COLOR_BUTTON_HOVER,
    "color_fill": DEFAULT_COLOR_FILL,
    "color_accent_icon": DEFAULT_COLOR_ACCENT_ICON,
    "color_accent_text": DEFAULT_COLOR_ACCENT_TEXT,
}


class BrandColorForm(forms.ModelForm):
    class Meta:
        model = BrandColorSettings
        fields = tuple(_COLOR_DEFAULTS.keys())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, fallback in _COLOR_DEFAULTS.items():
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

    def clean_color_accent_icon(self):
        return self._clean_hex("color_accent_icon", DEFAULT_COLOR_ACCENT_ICON)

    def clean_color_accent_text(self):
        return self._clean_hex("color_accent_text", DEFAULT_COLOR_ACCENT_TEXT)

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
                "description": "Картки, калькулятор (пакет / слайдер / сума), м’які салатові фони.",
                "fields": ("color_fill",),
            },
        ),
        (
            "Темні акценти",
            {
                "description": "Окремо: іконки/крапки/лапки та акцентний текст (ціни, посилання).",
                "fields": (
                    "color_accent_icon",
                    "color_accent_text",
                ),
            },
        ),
    )

    class Media:
        css = {"all": ("css/admin/brand_colors.css",)}
        js = ("js/admin/brand_colors.js",)
