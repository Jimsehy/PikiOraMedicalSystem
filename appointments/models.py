from django.conf import settings
from django.db import models
from django.db.models import Q


class Doctor(models.Model):
    name = models.CharField(max_length=120)
    specialty = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"Dr {self.name} — {self.specialty}"


class AppointmentSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="slots")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["date", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "date", "start_time"],
                name="unique_doctor_slot",
            )
        ]

    @property
    def is_booked(self):
        return self.appointments.filter(status="BOOKED").exists()

    def __str__(self):
        return f"{self.doctor.name} — {self.date} {self.start_time:%H:%M}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("BOOKED", "Booked"),
        ("CANCELLED", "Cancelled"),
        ("COMPLETED", "Completed"),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    slot = models.ForeignKey(
        AppointmentSlot,
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="BOOKED")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-slot__date", "-slot__start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["slot"],
                condition=Q(status="BOOKED"),
                name="one_active_booking_per_slot",
            )
        ]

    def __str__(self):
        return f"{self.patient.username} — {self.slot}"
