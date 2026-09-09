from __future__ import annotations

from django import forms
from django.forms import BaseModelFormSet, modelformset_factory

from .admin_guidelines import get_image_hint
from .admin_site_content_widgets import CmsAdminImageWidget, CmsAdminTextInputWidget
from .hero_slides import ensure_default_hero_slides
from .models import HeroSlide

try:
    from unfold.widgets import UnfoldAdminFileFieldWidget, UnfoldBooleanWidget
except Exception:  # pragma: no cover
    UnfoldAdminFileFieldWidget = forms.ClearableFileInput
    UnfoldBooleanWidget = forms.CheckboxInput


class HeroSlideForm(forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = (
            "image",
            "image_url",
            "video",
            "video_url",
            "alt_text",
            "is_active",
            "sort_order",
        )
        widgets = {
            "image": CmsAdminImageWidget(),
            "image_url": CmsAdminTextInputWidget(),
            "video": UnfoldAdminFileFieldWidget(),
            "video_url": CmsAdminTextInputWidget(),
            "alt_text": CmsAdminTextInputWidget(),
            "is_active": UnfoldBooleanWidget(),
            "sort_order": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].help_text = get_image_hint("hero")
        self.fields["image"].required = False
        self.fields["image_url"].required = False
        self.fields["video"].required = False
        self.fields["video_url"].required = False
        self.fields["alt_text"].required = False
        self.fields["is_active"].label = "Показувати на сайті"

    def clean(self):
        cleaned = super().clean()
        if self.cleaned_data.get("DELETE"):
            return cleaned
        image = cleaned.get("image")
        image_url = (cleaned.get("image_url") or "").strip()
        video = cleaned.get("video")
        video_url = (cleaned.get("video_url") or "").strip()
        alt_text = (cleaned.get("alt_text") or "").strip()
        has_image = bool(image) or bool(image_url) or bool(
            getattr(self.instance, "image", None)
        )
        has_video = bool(video) or bool(video_url) or bool(
            getattr(self.instance, "video", None)
        )
        if alt_text and not has_image and not has_video:
            self.add_error(
                "image", "Додайте фото/відео або посилання, якщо заповнено опис."
            )
        if not has_image and not has_video and not alt_text:
            cleaned["_skip"] = True
        return cleaned


class HeroSlideBaseFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()
        order = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data") or not form.cleaned_data:
                continue
            if form.cleaned_data.get("DELETE"):
                continue
            if form.cleaned_data.get("_skip"):
                continue
            form.cleaned_data["sort_order"] = order
            form.instance.sort_order = order
            order += 1


HeroSlideFormSet = modelformset_factory(
    HeroSlide,
    form=HeroSlideForm,
    formset=HeroSlideBaseFormSet,
    extra=1,
    can_delete=True,
)


def build_hero_slide_formset(data=None, files=None):
    ensure_default_hero_slides()
    qs = HeroSlide.objects.all().order_by("sort_order", "pk")
    return HeroSlideFormSet(
        data=data,
        files=files,
        queryset=qs,
        prefix="hero_slides",
    )


def save_hero_slide_formset(formset) -> None:
    instances = formset.save(commit=False)
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
        instance = form.save(commit=False)
        kept.append(instance)
    for idx, instance in enumerate(kept):
        instance.sort_order = idx
        instance.save()
