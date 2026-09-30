from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),
    path("doctors/", views.doctor_list, name="doctor_list"),
    path("doctors/add/", views.doctor_create, name="doctor_create"),
    path("doctors/<int:doctor_id>/edit/", views.doctor_edit, name="doctor_edit"),
    path("doctors/<int:doctor_id>/delete/", views.doctor_delete, name="doctor_delete"),
    path("slots/", views.slot_list_admin, name="slot_list_admin"),
    path("slots/add/", views.slot_create, name="slot_create"),
    path("slots/<int:slot_id>/edit/", views.slot_edit, name="slot_edit"),
    path("slots/<int:slot_id>/delete/", views.slot_delete, name="slot_delete"),
    path("appointments/", views.appointment_list_admin, name="appointment_list_admin"),
    path("appointments/<int:appointment_id>/edit/", views.appointment_edit_admin, name="appointment_edit_admin"),
    path("appointments/<int:appointment_id>/delete/", views.appointment_delete_admin, name="appointment_delete_admin"),
    path("patients/", views.patient_list, name="patient_list"),
    path("patients/<int:user_id>/toggle/", views.toggle_patient, name="toggle_patient"),
]
