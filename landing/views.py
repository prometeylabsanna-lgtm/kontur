import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .forms import LeadForm


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@require_GET
def home(request):
    return render(request, "landing/index.html")


@require_GET
def privacy(request):
    return render(request, "landing/privacy.html")


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
