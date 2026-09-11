from __future__ import annotations

from decimal import Decimal

from django import forms

from .admin_site_content_widgets import (
    CmsAdminNumberInputWidget,
    CmsAdminTextInputWidget,
)
from .google_places import extract_place_id, is_configured
from .models import SiteSettings


class CalculatorConfigForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = (
            "calc_area_min",
            "calc_area_max",
            "calc_billable_min",
            "calc_coef_to_30",
            "calc_coef_31_34",
            "calc_coef_35_39",
            "calc_pay_1",
            "calc_pay_2",
            "calc_pay_3",
            "calc_pay_4",
        )
        widgets = {
            "calc_area_min": CmsAdminNumberInputWidget(attrs={"min": 1, "step": 1}),
            "calc_area_max": CmsAdminNumberInputWidget(attrs={"min": 1, "step": 1}),
            "calc_billable_min": CmsAdminNumberInputWidget(attrs={"min": 1, "step": 1}),
            "calc_coef_to_30": CmsAdminNumberInputWidget(
                attrs={"min": 0, "step": "0.01"}
            ),
            "calc_coef_31_34": CmsAdminNumberInputWidget(
                attrs={"min": 0, "step": "0.01"}
            ),
            "calc_coef_35_39": CmsAdminNumberInputWidget(
                attrs={"min": 0, "step": "0.01"}
            ),
            "calc_pay_1": CmsAdminNumberInputWidget(
                attrs={"min": 0, "max": 1, "step": "0.01"}
            ),
            "calc_pay_2": CmsAdminNumberInputWidget(
                attrs={"min": 0, "max": 1, "step": "0.01"}
            ),
            "calc_pay_3": CmsAdminNumberInputWidget(
                attrs={"min": 0, "max": 1, "step": "0.01"}
            ),
            "calc_pay_4": CmsAdminNumberInputWidget(
                attrs={"min": 0, "max": 1, "step": "0.01"}
            ),
        }

    def clean(self):
        cleaned = super().clean()
        amin = cleaned.get("calc_area_min")
        amax = cleaned.get("calc_area_max")
        billable = cleaned.get("calc_billable_min")
        if amin is not None and amax is not None and amin >= amax:
            self.add_error("calc_area_max", "Максимум має бути більшим за мінімум.")
        if billable is not None and amin is not None and billable < amin:
            self.add_error(
                "calc_billable_min",
                "Розрахункова площа не може бути меншою за мінімум слайдера.",
            )
        pays = [
            cleaned.get("calc_pay_1"),
            cleaned.get("calc_pay_2"),
            cleaned.get("calc_pay_3"),
            cleaned.get("calc_pay_4"),
        ]
        if all(p is not None for p in pays):
            total = sum(pays, Decimal("0"))
            if total < Decimal("0.99") or total > Decimal("1.01"):
                self.add_error(
                    "calc_pay_1",
                    f"Сума часток має бути ≈ 1.00 (зараз {total}).",
                )
        return cleaned


class ProofRatingForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = (
            "google_place_id",
            "google_reviews_auto_sync",
            "google_rating",
            "google_reviews_count",
            "google_reviews_url",
        )
        widgets = {
            "google_place_id": CmsAdminTextInputWidget(
                attrs={"placeholder": "ChIJ… або посилання Google Maps"}
            ),
            "google_rating": forms.NumberInput(
                attrs={"min": 0, "max": 5, "step": "0.1"}
            ),
            "google_reviews_count": forms.NumberInput(attrs={"min": 0, "step": 1}),
            "google_reviews_url": CmsAdminTextInputWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        key_ok = is_configured()
        base = self.fields["google_place_id"].help_text or ""
        status = (
            "Ключ API знайдено в .env."
            if key_ok
            else "Ключ ще не задано: додайте GOOGLE_PLACES_API_KEY у .env і перезапустіть."
        )
        self.fields["google_place_id"].help_text = f"{base} {status}".strip()

    def clean_google_place_id(self):
        raw = (self.cleaned_data.get("google_place_id") or "").strip()
        if not raw:
            return ""
        extracted = extract_place_id(raw)
        if extracted:
            return extracted
        if raw.startswith("http://") or raw.startswith("https://"):
            raise forms.ValidationError(
                "У посиланні не знайдено Place ID (ChIJ…). "
                "Вставте Place ID з Google Business / Place ID Finder "
                "або URL з параметром place_id=."
            )
        return raw


def build_section_extra_form(section_slug: str, data=None):
    settings_obj = SiteSettings.get_solo()
    if section_slug == "calculator":
        return CalculatorConfigForm(data, instance=settings_obj, prefix="calc_cfg")
    if section_slug == "proof":
        return ProofRatingForm(data, instance=settings_obj, prefix="proof_rating")
    return None
