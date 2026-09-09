from __future__ import annotations

from django import forms
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.urls import reverse

from .admin_collections import build_section_collections, save_section_collections
from .admin_guidelines import get_image_hint, get_text_limit_hint
from .admin_site_content_widgets import (
    CmsAdminTextInputWidget,
    CmsAdminTextareaWidget,
)
from .admin_section_extras import build_section_extra_form
from .block_defaults import (
    BLOCK_CONTENT_TYPES,
    BLOCK_DEFAULTS,
    BLOCK_FIELD_LABELS,
    is_inline_key,
    is_multiline_key,
    is_visibility_key,
)
from .context_processors import SITE_BLOCKS_CACHE_KEY
from .models import SiteBlock, SiteSettings
from .privacy_text import (
    PRIVACY_BODY_HELP,
    html_to_plain,
    plain_to_html,
)
from .site_content_registry import ContentSection, get_section, iter_section_blocks

try:
    from unfold.widgets import UnfoldAdminFileFieldWidget, UnfoldBooleanWidget
except Exception:  # pragma: no cover
    UnfoldAdminFileFieldWidget = forms.ClearableFileInput
    UnfoldBooleanWidget = forms.CheckboxInput


def load_section_blocks(section: ContentSection) -> dict[str, SiteBlock]:
    result: dict[str, SiteBlock] = {}
    for page, key, label in iter_section_blocks(section):
        defaults = {
            "label": label or BLOCK_FIELD_LABELS.get((page, key), key),
            "content_type": BLOCK_CONTENT_TYPES.get((page, key), "text"),
            "text_html": BLOCK_DEFAULTS.get(
                (page, key), "1" if is_visibility_key(key) else ""
            ),
        }
        block, _ = SiteBlock.objects.get_or_create(
            page=page, key=key, defaults=defaults
        )
        result[key] = block
    return result


class SitePageContentForm(forms.Form):
    def __init__(self, section: ContentSection, blocks: dict[str, SiteBlock], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.section = section
        self.blocks = blocks

        if section.visibility_key:
            current = blocks.get(section.visibility_key)
            checked = True
            if current is not None:
                checked = current.text_html not in {"0", "false", "False", ""}
            self.fields["section_visible"] = forms.BooleanField(
                label="Показувати секцію на сайті",
                required=False,
                initial=checked,
                widget=UnfoldBooleanWidget(),
            )

        for page, key, label in iter_section_blocks(section):
            if section.visibility_key and key == section.visibility_key:
                continue
            block = blocks[key]
            content_type = BLOCK_CONTENT_TYPES.get((page, key), block.content_type)
            human = label or BLOCK_FIELD_LABELS.get((page, key), key)

            if is_visibility_key(key):
                self.fields[f"block__{page}__{key}__visible"] = forms.BooleanField(
                    label=human,
                    required=False,
                    initial=block.text_html not in {"0", "false", "False", ""},
                    widget=UnfoldBooleanWidget(),
                )
                continue

            if content_type == "image":
                self.fields[f"block__{page}__{key}__image"] = forms.ImageField(
                    label=human,
                    required=False,
                    widget=UnfoldAdminFileFieldWidget(),
                    help_text=get_image_hint("block_image"),
                )
                continue

            if content_type == "url":
                self.fields[f"block__{page}__{key}__link_url"] = forms.CharField(
                    label=f"{human} — посилання",
                    required=False,
                    initial=block.link_url,
                    widget=CmsAdminTextInputWidget(),
                )
                self.fields[f"block__{page}__{key}__link_label"] = forms.CharField(
                    label=f"{human} — текст на кнопці",
                    required=False,
                    initial=block.link_label,
                    widget=CmsAdminTextInputWidget(),
                )
                continue

            hint = get_text_limit_hint(key)
            help_text = hint or ""
            initial_text = block.text_html
            rows = 2
            if key == "privacy_body":
                initial_text = html_to_plain(block.text_html)
                help_text = PRIVACY_BODY_HELP
                rows = 16
            elif is_multiline_key(key):
                rows = 4

            if is_inline_key(key):
                widget = CmsAdminTextInputWidget()
            else:
                widget = CmsAdminTextareaWidget(attrs={"rows": rows})
            self.fields[f"block__{page}__{key}__text_html"] = forms.CharField(
                label=human,
                required=False,
                initial=initial_text,
                widget=widget,
                help_text=help_text,
            )

    def save(self) -> None:
        section = self.section
        if section.visibility_key and "section_visible" in self.cleaned_data:
            visible = "1" if self.cleaned_data["section_visible"] else "0"
            block = self.blocks[section.visibility_key]
            block.text_html = visible
            block.save(update_fields=["text_html"])

        for name, value in self.cleaned_data.items():
            if not name.startswith("block__"):
                continue
            parts = name.split("__")
            if len(parts) != 4:
                continue
            _, page, key, suffix = parts
            block = self.blocks.get(key)
            if block is None:
                continue
            if suffix == "visible":
                block.text_html = "1" if value else "0"
                block.save(update_fields=["text_html"])
            elif suffix == "text_html":
                text = value or ""
                if key == "privacy_body":
                    text = plain_to_html(text)
                block.text_html = text
                block.save(update_fields=["text_html"])
            elif suffix == "image":
                if value:
                    block.image = value
                    block.save(update_fields=["image"])
            elif suffix == "link_url":
                block.link_url = value or ""
                block.save(update_fields=["link_url"])
            elif suffix == "link_label":
                block.link_label = value or ""
                block.save(update_fields=["link_label"])

        cache.delete(SITE_BLOCKS_CACHE_KEY)


def build_admin_context(request, model_admin, extra: dict) -> dict:
    ctx = {
        **model_admin.admin_site.each_context(request),
        **extra,
    }
    return ctx


def _grouped_fields(form: SitePageContentForm, section: ContentSection) -> list[dict]:
    groups = []
    used = set()
    if "section_visible" in form.fields:
        groups.append(
            {
                "title": "Видимість",
                "description": "",
                "fields": [form["section_visible"]],
            }
        )
        used.add("section_visible")

    for group in section.field_groups:
        bound = []
        for key in group.keys:
            for name, field in form.fields.items():
                if name in used:
                    continue
                if f"__{key}__" in name:
                    bound.append(form[name])
                    used.add(name)
        if bound:
            groups.append(
                {
                    "title": group.title,
                    "description": group.description,
                    "fields": bound,
                }
            )

    leftover = [form[name] for name in form.fields if name not in used]
    if leftover:
        groups.append({"title": "Інше", "description": "", "fields": leftover})
    return groups


def site_content_section_view(request, page_slug: str, section_slug: str, model_admin):
    section = get_section(page_slug, section_slug)
    if section is None:
        messages.error(request, "Секцію не знайдено.")
        return redirect("admin:index")

    SiteSettings.get_solo()
    blocks = load_section_blocks(section)
    collections = []
    extra_form = None

    if request.method == "POST":
        form = SitePageContentForm(section, blocks, request.POST, request.FILES)
        collections = build_section_collections(
            section.slug, data=request.POST, files=request.FILES
        )
        extra_form = build_section_extra_form(section.slug, data=request.POST)
        valid = form.is_valid() and all(c["formset"].is_valid() for c in collections)
        if extra_form is not None:
            valid = valid and extra_form.is_valid()
        if valid:
            form.save()
            save_section_collections(collections)
            if extra_form is not None:
                extra_form.save()
            messages.success(request, "Збережено.")
            return redirect(request.path)
    else:
        form = SitePageContentForm(section, blocks)
        collections = build_section_collections(section.slug)
        extra_form = build_section_extra_form(section.slug)

    media = form.media
    for item in collections:
        media = media + item["formset"].media
    if extra_form is not None:
        media = media + extra_form.media

    opts = model_admin.model._meta
    context = build_admin_context(
        request,
        model_admin,
        {
            "title": section.title,
            "section": section,
            "form": form,
            "field_groups": _grouped_fields(form, section),
            "collections": collections,
            "extra_form": extra_form,
            "extra_form_title": (
                "Параметри формули"
                if section.slug == "calculator"
                else "Рейтинг Google"
                if section.slug == "proof"
                else ""
            ),
            "opts": opts,
            "original": SiteSettings.get_solo(),
            "has_view_permission": True,
            "has_editable_inline_admin_formsets": False,
            "show_save": True,
            "media": media,
        },
    )
    return render(request, "admin/landing/site_content_page.html", context)
