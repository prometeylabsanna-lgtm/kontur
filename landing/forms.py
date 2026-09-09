import re

from django import forms

from .models import Lead


def normalize_ua_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if digits.startswith("380") and len(digits) == 12:
        return f"+{digits}"
    if digits.startswith("0") and len(digits) == 10:
        return f"+38{digits}"
    return (value or "").strip()


def is_ua_phone(value: str) -> bool:
    digits = re.sub(r"\D", "", value or "")
    return (digits.startswith("380") and len(digits) == 12) or (
        digits.startswith("0") and len(digits) == 10
    )


class LeadForm(forms.ModelForm):
    agree = forms.BooleanField(required=True)

    class Meta:
        model = Lead
        fields = (
            "name",
            "phone",
            "context",
            "package",
            "object_type",
            "area",
            "calc_summary",
            "utm_source",
            "utm_medium",
            "utm_campaign",
        )

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if len(name) < 2:
            raise forms.ValidationError("Вкажіть ім’я")
        return name

    def clean_phone(self):
        raw = (self.cleaned_data.get("phone") or "").strip()
        if not is_ua_phone(raw):
            raise forms.ValidationError("Вкажіть номер у форматі України")
        return normalize_ua_phone(raw)

    def clean_agree(self):
        if not self.cleaned_data.get("agree"):
            raise forms.ValidationError("Потрібна згода з політикою")
        return True

    def clean_area(self):
        area = self.cleaned_data.get("area")
        if area in ("", None):
            return None
        return area
