from django.contrib import admin
from unfold.admin import ModelAdmin

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
    list_filter = ("status", "package", "object_type", "created_at")
    list_filter_submit = True
    search_fields = ("name", "phone", "context", "calc_summary")
    readonly_fields = ("created_at", "updated_at", "client_ip")
    list_editable = ("status",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


register_site_content_section_admins()
