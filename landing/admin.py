from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
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
    search_fields = ("name", "phone", "context", "calc_summary")
    readonly_fields = ("created_at", "updated_at", "client_ip")
    list_editable = ("status",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
