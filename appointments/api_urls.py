from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    DoctorViewSet, AppointmentSlotViewSet, AppointmentViewSet,
    PatientViewSet, RegisterAPIView, LoginAPIView, AdminSummaryAPIView,
    logout_api,
)

router = DefaultRouter()
router.register("doctors", DoctorViewSet, basename="doctor")
router.register("slots", AppointmentSlotViewSet, basename="slot")
router.register("appointments", AppointmentViewSet, basename="appointment")
router.register("patients", PatientViewSet, basename="patient")

urlpatterns = [
    path("auth/register/", RegisterAPIView.as_view(), name="api-register"),
    path("auth/login/", LoginAPIView.as_view(), name="api-login"),
    path("auth/logout/", logout_api, name="api-logout"),
    path("admin/summary/", AdminSummaryAPIView.as_view(), name="api-admin-summary"),
    path("", include(router.urls)),
]
