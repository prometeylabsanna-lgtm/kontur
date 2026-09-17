"""Окрема сторінка «Недавні дії» в адмінці (замість правого віджета на index)."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.template.response import TemplateResponse
from django.urls import path

RECENT_ACTIONS_LIMIT = 100


def recent_actions_view(request):
    entries = list(
        LogEntry.objects.filter(user_id=request.user.pk)
        .select_related("content_type")
        .order_by("-action_time")[:RECENT_ACTIONS_LIMIT]
    )
    context = {
        **admin.site.each_context(request),
        "title": "Недавні дії",
        "subtitle": None,
        "entries": entries,
    }
    return TemplateResponse(request, "admin/landing/recent_actions.html", context)


def register_recent_actions_url():
    """Підключає URL до Unfold AdminSite через extra_urls."""

    site = admin.site

    def extra_urls():
        return [
            path(
                "recent-actions/",
                site.admin_view(recent_actions_view),
                name="recent_actions",
            ),
        ]

    site.extra_urls = extra_urls
