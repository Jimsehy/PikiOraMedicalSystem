from django.urls import path

from . import views

urlpatterns = [
    path("", views.slot_list, name="slot_list"),
    path("book/<int:slot_id>/", views.book_appointment, name="book_appointment"),
    path("mine/", views.my_appointments, name="my_appointments"),
    path("<int:appointment_id>/edit/", views.edit_appointment, name="edit_appointment"),
    path("<int:appointment_id>/cancel/", views.cancel_appointment, name="cancel_appointment"),
]
