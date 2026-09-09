from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from landing.views import decoy_admin

urlpatterns = [
    path("kontur-plus-cms/", admin.site.urls),
    path("admin", decoy_admin),
    path("admin/", decoy_admin),
    path("admin/<path:rest>", decoy_admin),
    path("tinymce/", include("tinymce.urls")),
    path("", include("landing.urls")),
]

handler400 = "landing.views.bad_request"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
