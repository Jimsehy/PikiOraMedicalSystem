from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Doctor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("specialty", models.CharField(max_length=120)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("bio", models.TextField(blank=True)),
                ("active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="AppointmentSlot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("active", models.BooleanField(default=True)),
                ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="slots", to="appointments.doctor")),
            ],
            options={"ordering": ["date", "start_time"]},
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("BOOKED", "Booked"), ("CANCELLED", "Cancelled"), ("COMPLETED", "Completed")], default="BOOKED", max_length=20)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="appointments", to=settings.AUTH_USER_MODEL)),
                ("slot", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="appointments", to="appointments.appointmentslot")),
            ],
            options={"ordering": ["-slot__date", "-slot__start_time"]},
        ),
        migrations.AddConstraint(
            model_name="appointmentslot",
            constraint=models.UniqueConstraint(fields=("doctor", "date", "start_time"), name="unique_doctor_slot"),
        ),
        migrations.AddConstraint(
            model_name="appointment",
            constraint=models.UniqueConstraint(condition=Q(("status", "BOOKED")), fields=("slot",), name="one_active_booking_per_slot"),
        ),
    ]
