"""Formsets карток для CMS-секцій (у тій же панелі, що й тексти)."""

from __future__ import annotations

from django import forms
from django.forms import BaseModelFormSet, modelformset_factory

from .admin_guidelines import get_image_hint
from .admin_hero_slides import build_hero_slide_formset
from .admin_site_content_widgets import (
    CmsAdminImageWidget,
    CmsAdminTextInputWidget,
    CmsAdminTextareaWidget,
)
from .hero_slides import ensure_default_hero_slides
from .models import (
    AdvantageItem,
    CaseItem,
    DesignFeature,
    FAQItem,
    PackageItem,
    ReviewItem,
    StyleItem,
)

try:
    from unfold.widgets import (
        UnfoldAdminSelectWidget,
        UnfoldBooleanWidget,
    )
except Exception:  # pragma: no cover
    UnfoldAdminSelectWidget = forms.Select
    UnfoldBooleanWidget = forms.CheckboxInput


class OrderedBaseFormSet(BaseModelFormSet):
    skip_flag = "_skip"

    def clean(self):
        super().clean()
        order = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data") or not form.cleaned_data:
                continue
            if form.cleaned_data.get("DELETE"):
                continue
            if form.cleaned_data.get(self.skip_flag):
                continue
            form.cleaned_data["sort_order"] = order
            form.instance.sort_order = order
            order += 1


def _save_ordered_formset(formset) -> None:
    formset.save(commit=False)
    for obj in formset.deleted_objects:
        obj.delete()
    kept = []
    for form in formset.forms:
        if not hasattr(form, "cleaned_data") or not form.cleaned_data:
            continue
        if form.cleaned_data.get("DELETE"):
            continue
        if form.cleaned_data.get("_skip"):
            continue
        kept.append(form.save(commit=False))
    for idx, instance in enumerate(kept):
        instance.sort_order = idx
        instance.save()


def _make_formset(model, form, prefix, extra=1):
    return modelformset_factory(
        model,
        form=form,
        formset=OrderedBaseFormSet,
        extra=extra,
        can_delete=True,
    )


# --- Advantages ---
class AdvantageForm(forms.ModelForm):
    class Meta:
        model = AdvantageItem
        fields = (
            "kind",
            "icon",
            "title",
            "text",
            "image",
            "image_alt",
            "cta_label",
            "cta_href",
            "is_active",
            "sort_order",
        )
        widgets = {
            "kind": UnfoldAdminSelectWidget(),
            "icon": UnfoldAdminSelectWidget(),
            "title": CmsAdminTextInputWidget(),
            "text": CmsAdminTextareaWidget(attrs={"rows": 3}),
            "image": CmsAdminImageWidget(),
            "image_alt": CmsAdminTextInputWidget(),
            "cta_label": CmsAdminTextInputWidget(),
            "cta_href": CmsAdminTextInputWidget(),
            "is_active": UnfoldBooleanWidget(),
            "sort_order": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].required = False
        self.fields["image"].help_text = get_image_hint("advantage")
        self.fields["is_active"].label = "Показувати"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        title = (cleaned.get("title") or "").strip()
        if not title and not self.instance.pk:
            cleaned["_skip"] = True
        return cleaned


AdvantageFormSet = _make_formset(AdvantageItem, AdvantageForm, "advantages")


def build_advantages_formset(data=None, files=None):
    return AdvantageFormSet(
        data=data,
        files=files,
        queryset=AdvantageItem.objects.all().order_by("sort_order", "pk"),
        prefix="advantages",
    )


# --- Packages ---
class PackageForm(forms.ModelForm):
    class Meta:
        model = PackageItem
        fields = (
            "name",
            "description",
            "price",
            "price_unit",
            "features",
            "badge",
            "cta_label",
            "is_recommended",
            "is_active",
            "sort_order",
        )
        widgets = {
            "name": CmsAdminTextInputWidget(),
            "description": CmsAdminTextareaWidget(attrs={"rows": 2}),
            "price": CmsAdminTextInputWidget(),
            "price_unit": CmsAdminTextInputWidget(),
            "features": CmsAdminTextareaWidget(attrs={"rows": 4}),
            "badge": CmsAdminTextInputWidget(),
            "cta_label": CmsAdminTextInputWidget(),
            "is_recommended": UnfoldBooleanWidget(),
            "is_active": UnfoldBooleanWidget(),
            "sort_order": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["is_active"].label = "Показувати"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        if not (cleaned.get("name") or "").strip() and not self.instance.pk:
            cleaned["_skip"] = True
        return cleaned


PackageFormSet = _make_formset(PackageItem, PackageForm, "packages")


def build_packages_formset(data=None, files=None):
    return PackageFormSet(
        data=data,
        files=files,
        queryset=PackageItem.objects.all().order_by("sort_order", "pk"),
        prefix="packages",
    )


# --- Design features ---
class DesignFeatureForm(forms.ModelForm):
    class Meta:
        model = DesignFeature
        fields = ("text", "is_active", "sort_order")
        widgets = {
            "text": CmsAdminTextInputWidget(),
            "is_active": UnfoldBooleanWidget(),
            "sort_order": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["is_active"].label = "Показувати"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        if not (cleaned.get("text") or "").strip() and not self.instance.pk:
            cleaned["_skip"] = True
        return cleaned


DesignFeatureFormSet = _make_formset(DesignFeature, DesignFeatureForm, "design_features")


def build_design_features_formset(data=None, files=None):
    return DesignFeatureFormSet(
        data=data,
        files=files,
        queryset=DesignFeature.objects.all().order_by("sort_order", "pk"),
        prefix="design_features",
    )


# --- Styles ---
class StyleForm(forms.ModelForm):
    class Meta:
        model = StyleItem
        fields = ("title", "text", "image", "image_url", "is_active", "sort_order")
        widgets = {
            "title": CmsAdminTextInputWidget(),
            "text": CmsAdminTextareaWidget(attrs={"rows": 2}),
            "image": CmsAdminImageWidget(),
            "image_url": CmsAdminTextInputWidget(),
            "is_active": UnfoldBooleanWidget(),
            "sort_order": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].required = False
        self.fields["is_active"].label = "Показувати"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        if not (cleaned.get("title") or "").strip() and not self.instance.pk:
            cleaned["_skip"] = True
        return cleaned


StyleFormSet = _make_formset(StyleItem, StyleForm, "styles")


def build_styles_formset(data=None, files=None):
    return StyleFormSet(
        data=data,
        files=files,
        queryset=StyleItem.objects.all().order_by("sort_order", "pk"),
        prefix="styles",
    )


# --- Reviews ---
class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewItem
        fields = ("text", "name", "meta", "is_active", "sort_order")
        widgets = {
            "text": CmsAdminTextareaWidget(attrs={"rows": 3}),
            "name": CmsAdminTextInputWidget(),
            "meta": CmsAdminTextInputWidget(),
            "is_active": UnfoldBooleanWidget(),
            "sort_order": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["is_active"].label = "Показувати"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        if not (cleaned.get("text") or "").strip() and not self.instance.pk:
            cleaned["_skip"] = True
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.source = ReviewItem.Source.MANUAL
        if commit:
            obj.save()
        return obj


ReviewFormSet = _make_formset(ReviewItem, ReviewForm, "reviews")


def build_reviews_formset(data=None, files=None):
    return ReviewFormSet(
        data=data,
        files=files,
        queryset=ReviewItem.objects.filter(source=ReviewItem.Source.MANUAL).order_by(
            "sort_order", "pk"
        ),
        prefix="reviews",
    )


# --- Cases ---
class CaseForm(forms.ModelForm):
    class Meta:
        model = CaseItem
        fields = (
            "title",
            "location",
            "text",
            "image",
            "image_alt",
            "tags",
            "is_active",
            "sort_order",
        )
        widgets = {
            "title": CmsAdminTextInputWidget(),
            "location": CmsAdminTextInputWidget(),
            "text": CmsAdminTextareaWidget(attrs={"rows": 3}),
            "image": CmsAdminImageWidget(),
            "image_alt": CmsAdminTextInputWidget(),
            "tags": CmsAdminTextareaWidget(attrs={"rows": 3}),
            "is_active": UnfoldBooleanWidget(),
            "sort_order": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].required = False
        self.fields["image"].help_text = get_image_hint("case")
        self.fields["is_active"].label = "Показувати"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        if not (cleaned.get("title") or "").strip() and not self.instance.pk:
            cleaned["_skip"] = True
        return cleaned


CaseFormSet = _make_formset(CaseItem, CaseForm, "cases")


def build_cases_formset(data=None, files=None):
    return CaseFormSet(
        data=data,
        files=files,
        queryset=CaseItem.objects.all().order_by("sort_order", "pk"),
        prefix="cases",
    )


# --- FAQ ---
class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQItem
        fields = ("question", "answer", "is_active", "sort_order")
        widgets = {
            "question": CmsAdminTextInputWidget(),
            "answer": CmsAdminTextareaWidget(attrs={"rows": 3}),
            "is_active": UnfoldBooleanWidget(),
            "sort_order": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["is_active"].label = "Показувати"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        if not (cleaned.get("question") or "").strip() and not self.instance.pk:
            cleaned["_skip"] = True
        return cleaned


FAQFormSet = _make_formset(FAQItem, FAQForm, "faq_items")


def build_faq_formset(data=None, files=None):
    return FAQFormSet(
        data=data,
        files=files,
        queryset=FAQItem.objects.all().order_by("sort_order", "pk"),
        prefix="faq_items",
    )


# section.slug → list of collection configs
SECTION_COLLECTIONS: dict[str, tuple[dict, ...]] = {
    "hero": (
        {
            "key": "hero_slides",
            "title": "Фото банера",
            "hint": "Додавайте фото, змінюйте порядок. Можна файл або посилання.",
            "add_label": "Додати фото",
            "build": build_hero_slide_formset,
            "save": _save_ordered_formset,
        },
    ),
    "advantages": (
        {
            "key": "advantages",
            "title": "Картки переваг",
            "hint": "Текст, іконка, фото та видимість кожної картки.",
            "add_label": "Додати картку",
            "build": build_advantages_formset,
            "save": _save_ordered_formset,
        },
    ),
    "packages": (
        {
            "key": "packages",
            "title": "Картки пакетів",
            "hint": "Назва, ціна, склад і кнопка для кожного пакету.",
            "add_label": "Додати пакет",
            "build": build_packages_formset,
            "save": _save_ordered_formset,
        },
    ),
    "design": (
        {
            "key": "design_features",
            "title": "Пункти списку",
            "hint": "Що входить у дизайн-проєкт — по одному рядку.",
            "add_label": "Додати пункт",
            "build": build_design_features_formset,
            "save": _save_ordered_formset,
        },
    ),
    "styles": (
        {
            "key": "styles",
            "title": "Картки стилів",
            "hint": "Назва, опис і фото кожного стилю.",
            "add_label": "Додати стиль",
            "build": build_styles_formset,
            "save": _save_ordered_formset,
        },
    ),
    "proof": (
        {
            "key": "reviews",
            "title": "Резервні відгуки (вручну)",
            "hint": (
                "Показуються, якщо ще немає синхронізованих Google-відгуків. "
                "Після успішного sync з Places на сайті будуть картки з Google."
            ),
            "add_label": "Додати відгук",
            "build": build_reviews_formset,
            "save": _save_ordered_formset,
        },
        {
            "key": "cases",
            "title": "Кейси",
            "hint": "Фото, заголовок, опис і теги робіт.",
            "add_label": "Додати кейс",
            "build": build_cases_formset,
            "save": _save_ordered_formset,
        },
    ),
    "faq": (
        {
            "key": "faq_items",
            "title": "Питання та відповіді",
            "hint": "Додавайте й змінюйте питання для клієнтів.",
            "add_label": "Додати питання",
            "build": build_faq_formset,
            "save": _save_ordered_formset,
        },
    ),
}


def build_section_collections(section_slug: str, data=None, files=None) -> list[dict]:
    configs = SECTION_COLLECTIONS.get(section_slug, ())
    if section_slug == "hero":
        ensure_default_hero_slides()
    result = []
    for cfg in configs:
        formset = cfg["build"](data=data, files=files)
        result.append({**cfg, "formset": formset})
    return result


def save_section_collections(collections: list[dict]) -> None:
    for item in collections:
        item["save"](item["formset"])
