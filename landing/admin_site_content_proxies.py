from __future__ import annotations

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from unfold.admin import ModelAdmin

from .admin_site_content import site_content_section_view
from .admin_site_content_widgets import apply_readable_widget
from .models import SiteSettings
from . import models_proxies as proxies


class SingletonModelAdminMixin:
    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = self.model.objects.first()
        if obj is None:
            obj = self.model.objects.create(pk=1)
        return HttpResponseRedirect(
            reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                args=[obj.pk],
            )
        )


class ReadableUnfoldFieldsMixin:
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield is not None and formfield.widget is not None:
            apply_readable_widget(formfield.widget)
        return formfield


class SiteContentSectionAdmin(SingletonModelAdminMixin, ModelAdmin):
    page_slug: str = ""
    section_slug: str = ""

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return site_content_section_view(
            request,
            self.page_slug,
            self.section_slug,
            model_admin=self,
        )


_SECTION_MODELS = (
    (proxies.SiteHeaderSettings, "site", "header"),
    (proxies.HomeHeroSettings, "home", "hero"),
    (proxies.HomeAdvantagesSettings, "home", "advantages"),
    (proxies.HomePackagesSettings, "home", "packages"),
    (proxies.HomeDesignSettings, "home", "design"),
    (proxies.HomeStylesSettings, "home", "styles"),
    (proxies.HomeCalculatorSettings, "home", "calculator"),
    (proxies.HomeProofSettings, "home", "proof"),
    (proxies.HomeFaqSettings, "home", "faq"),
    (proxies.SiteFooterSettings, "site", "footer"),
    (proxies.SiteModalSettings, "site", "modal"),
    (proxies.PrivacyPageSettings, "privacy", "privacy"),
)


def register_site_content_section_admins():
    for model, page_slug, section_slug in _SECTION_MODELS:
        admin_class = type(
            f"{model.__name__}Admin",
            (SiteContentSectionAdmin,),
            {
                "page_slug": page_slug,
                "section_slug": section_slug,
            },
        )
        try:
            admin.site.register(model, admin_class)
        except admin.sites.AlreadyRegistered:
            pass


@admin.register(SiteSettings)
class SiteSettingsAdmin(ReadableUnfoldFieldsMixin, SingletonModelAdminMixin, ModelAdmin):
    fieldsets = (
        (
            "Основне",
            {
                "fields": (
                    "site_name",
                    "brand_desc",
                    "phone_display",
                    "phone_tel",
                    "email",
                    "city",
                    "work_hours",
                )
            },
        ),
        ("Соцмережі", {"fields": ("instagram_url", "telegram_url")}),
        ("Пошук у Google", {"fields": ("meta_description",)}),
    )
