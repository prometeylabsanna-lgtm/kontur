from django.urls import path

from . import views

app_name = "landing"

urlpatterns = [
    path("", views.home, name="home"),
    path("privacy/", views.privacy, name="privacy"),
    path("favicon.ico", views.favicon_ico, name="favicon_ico"),
    path("favicon-<int:size>.png", views.favicon_png, name="favicon_png"),
    path("api/leads/", views.lead_create, name="lead_create"),
]
