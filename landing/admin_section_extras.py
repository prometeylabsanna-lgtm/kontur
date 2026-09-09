"""Extra ModelForms for CMS sections (calculator formula, Google rating)."""

from __future__ import annotations

from decimal import Decimal

from django import forms

from .admin_site_content_widgets import CmsAdminTextInputWidget
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
            "calc_area_min": forms.NumberInput(attrs={"min": 1, "step": 1}),
            "calc_area_max": forms.NumberInput(attrs={"min": 1, "step": 1}),
            "calc_billable_min": forms.NumberInput(attrs={"min": 1, "step": 1}),
            "calc_coef_to_30": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "calc_coef_31_34": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "calc_coef_35_39": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "calc_pay_1": forms.NumberInput(attrs={"min": 0, "max": 1, "step": "0.01"}),
            "calc_pay_2": forms.NumberInput(attrs={"min": 0, "max": 1, "step": "0.01"}),
            "calc_pay_3": forms.NumberInput(attrs={"min": 0, "max": 1, "step": "0.01"}),
            "calc_pay_4": forms.NumberInput(attrs={"min": 0, "max": 1, "step": "0.01"}),
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
            "google_rating",
            "google_reviews_count",
            "google_reviews_url",
        )
        widgets = {
            "google_rating": forms.NumberInput(
                attrs={"min": 0, "max": 5, "step": "0.1"}
            ),
            "google_reviews_count": forms.NumberInput(attrs={"min": 0, "step": 1}),
            "google_reviews_url": CmsAdminTextInputWidget(),
        }


def build_section_extra_form(section_slug: str, data=None):
    settings_obj = SiteSettings.get_solo()
    if section_slug == "calculator":
        return CalculatorConfigForm(data, instance=settings_obj, prefix="calc_cfg")
    if section_slug == "proof":
        return ProofRatingForm(data, instance=settings_obj, prefix="proof_rating")
    return None
