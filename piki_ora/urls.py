from django.contrib.auth import views as auth_views
from django.urls import include, path

from appointments import views as appointment_views

urlpatterns = [
    path("", appointment_views.home, name="home"),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/", include("appointments.auth_urls")),
    path("appointments/", include("appointments.urls")),
    path("dashboard/", include("dashboard.urls")),
]
