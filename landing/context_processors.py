from django.conf import settings


def site_contacts(request):
    return {
        "SITE_PHONE_DISPLAY": settings.SITE_PHONE_DISPLAY,
        "SITE_PHONE_TEL": settings.SITE_PHONE_TEL,
        "SITE_CITY": settings.SITE_CITY,
        "SITE_HOURS": settings.SITE_HOURS,
        "SITE_EMAIL": settings.SITE_EMAIL,
        "SITE_INSTAGRAM": settings.SITE_INSTAGRAM,
        "SITE_TELEGRAM": settings.SITE_TELEGRAM,
    }
