from django.contrib import admin
from unfold.admin import ModelAdmin

from . import admin_brand_colors  # noqa: F401
from .admin_lead_filters import (
    CreatedDateDropdownFilter,
    ObjectTypeDropdownFilter,
    PackageDropdownFilter,
    StatusDropdownFilter,
)
from .admin_site_content_proxies import register_site_content_section_admins
from .models import Lead


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
    list_filter = (
        ("status", StatusDropdownFilter),
        PackageDropdownFilter,
        ObjectTypeDropdownFilter,
        CreatedDateDropdownFilter,
    )
    list_filter_submit = False
    list_filter_sheet = False
    list_filter_options = {
        "status": {"horizontal": True, "label": "Статус"},
        "package": {"horizontal": True, "label": "Пакет"},
        "object_type": {"horizontal": True, "label": "Тип об’єкта"},
        "created": {"horizontal": True, "label": "Дата"},
    }
    search_fields = ("name", "phone", "context", "calc_summary")
    readonly_fields = ("created_at", "updated_at", "client_ip")
    list_editable = ("status",)
    ordering = ("-created_at",)


register_site_content_section_admins()
