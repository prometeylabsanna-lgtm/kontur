import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .favicon import render_favicon_ico, render_favicon_png, resolve_favicon_color
from .forms import LeadForm
from .google_places import public_reviews_queryset
from .hero_slides import get_hero_slides
from .models import (
    AdvantageItem,
    CaseItem,
    DesignFeature,
    FAQItem,
    PackageItem,
    StyleItem,
)


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _landing_lists():
    return {
        "hero_slides": get_hero_slides(),
        "advantages": list(
            AdvantageItem.objects.filter(is_active=True).order_by("sort_order", "pk")
        ),
        "packages": list(
            PackageItem.objects.filter(is_active=True).order_by("sort_order", "pk")
        ),
        "design_features": list(
            DesignFeature.objects.filter(is_active=True).order_by("sort_order", "pk")
        ),
        "styles": list(
            StyleItem.objects.filter(is_active=True).order_by("sort_order", "pk")
        ),
        "reviews": list(public_reviews_queryset()),
        "cases": list(
            CaseItem.objects.filter(is_active=True).order_by("sort_order", "pk")
        ),
        "faq_items": list(
            FAQItem.objects.filter(is_active=True).order_by("sort_order", "pk")
        ),
    }


@require_GET
def home(request):
    return render(request, "landing/index.html", _landing_lists())


@require_GET
def privacy(request):
    return render(request, "landing/privacy.html")


@require_GET
def favicon_png(request, size: int):
    color = resolve_favicon_color()
    payload = render_favicon_png(color, size)
    response = HttpResponse(payload, content_type="image/png")
    response["Cache-Control"] = "public, max-age=604800, immutable"
    return response


@require_GET
def favicon_ico(request):
    color = resolve_favicon_color()
    payload = render_favicon_ico(color)
    response = HttpResponse(payload, content_type="image/x-icon")
    response["Cache-Control"] = "public, max-age=604800, immutable"
    return response


def bad_request(request, exception=None):
    return render(request, "errors/400.html", status=400)


def decoy_admin(request, rest=""):
    return bad_request(request)


@require_POST
def lead_create(request):
    if request.content_type and "application/json" in request.content_type:
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse(
                {"ok": False, "errors": {"__all__": ["Некоректний запит"]}},
                status=400,
            )
    else:
        payload = request.POST.dict()

    form = LeadForm(payload)
    if not form.is_valid():
        errors = {
            field: [str(e) for e in errs] for field, errs in form.errors.items()
        }
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    lead = form.save(commit=False)
    lead.client_ip = _client_ip(request)
    lead.save()
    return JsonResponse({"ok": True, "id": lead.pk})
