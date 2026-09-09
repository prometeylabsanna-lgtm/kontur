from django.contrib import admin
from unfold.admin import ModelAdmin

from .admin_site_content_proxies import register_site_content_section_admins
from .models import (
    AdvantageItem,
    CaseItem,
    DesignFeature,
    FAQItem,
    Lead,
    PackageItem,
    ReviewItem,
    StyleItem,
)


@admin.register(Lead)
class LeadAdmin(ModelAdmin):
    list_display = (
        "created_at",
        "name",
        "phone",
        "status",
        "context",
        "package",
        "object_type",
        "area",
    )
    list_filter = ("status", "package", "object_type", "created_at")
    list_filter_submit = True
    search_fields = ("name", "phone", "context", "calc_summary")
    readonly_fields = ("created_at", "updated_at", "client_ip")
    list_editable = ("status",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(AdvantageItem)
class AdvantageItemAdmin(ModelAdmin):
    list_display = ("title", "kind", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("kind", "is_active")
    search_fields = ("title", "text")
    ordering_field = "sort_order"
    exclude = ("image_static",)
    fields = (
        "kind",
        "title",
        "text",
        "image",
        "image_alt",
        "cta_label",
        "cta_href",
        "sort_order",
        "is_active",
    )


@admin.register(PackageItem)
class PackageItemAdmin(ModelAdmin):
    list_display = ("name", "price", "is_recommended", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active", "is_recommended")
    list_filter = ("is_active", "is_recommended")
    search_fields = ("name", "description")
    ordering_field = "sort_order"


@admin.register(DesignFeature)
class DesignFeatureAdmin(ModelAdmin):
    list_display = ("text", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("text",)
    ordering_field = "sort_order"


@admin.register(StyleItem)
class StyleItemAdmin(ModelAdmin):
    list_display = ("title", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("title", "text")
    ordering_field = "sort_order"
    fields = ("title", "text", "image", "image_url", "sort_order", "is_active")


@admin.register(ReviewItem)
class ReviewItemAdmin(ModelAdmin):
    list_display = ("name", "meta", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("name", "text", "meta")
    ordering_field = "sort_order"


@admin.register(CaseItem)
class CaseItemAdmin(ModelAdmin):
    list_display = ("title", "location", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("title", "location", "text")
    ordering_field = "sort_order"
    exclude = ("image_static",)
    fields = (
        "title",
        "location",
        "text",
        "image",
        "image_alt",
        "tags",
        "sort_order",
        "is_active",
    )


@admin.register(FAQItem)
class FAQItemAdmin(ModelAdmin):
    list_display = ("question", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("question", "answer")
    ordering_field = "sort_order"


register_site_content_section_admins()
