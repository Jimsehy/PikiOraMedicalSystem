from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),  # Django admin is for backend maintenance only.
    path("api/", include("appointments.api_urls")),
]
