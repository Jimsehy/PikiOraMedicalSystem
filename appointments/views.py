from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import AppointmentForm, RegistrationForm
from .models import Appointment, AppointmentSlot, Doctor


def home(request):
    return render(request, "home.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created.")
            return redirect("slot_list")
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


def slot_list(request):
    today = timezone.localdate()
    slots = (
        AppointmentSlot.objects
        .filter(active=True, doctor__active=True, date__gte=today)
        .select_related("doctor")
        .prefetch_related(
            Prefetch(
                "appointments",
                queryset=Appointment.objects.filter(status="BOOKED"),
            )
        )
    )
    return render(request, "appointments/slot_list.html", {"slots": slots})


@login_required
@transaction.atomic
def book_appointment(request, slot_id):
    slot = get_object_or_404(
        AppointmentSlot.objects.select_for_update().select_related("doctor"),
        pk=slot_id,
        active=True,
        doctor__active=True,
    )

    if slot.date < timezone.localdate():
        messages.error(request, "This appointment date has passed.")
        return redirect("slot_list")

    if Appointment.objects.filter(slot=slot, status="BOOKED").exists():
        messages.error(request, "That appointment slot has already been booked.")
        return redirect("slot_list")

    if Appointment.objects.filter(
        patient=request.user, slot=slot, status="BOOKED"
    ).exists():
        messages.info(request, "You already have this appointment.")
        return redirect("my_appointments")

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.slot = slot
            appointment.status = "BOOKED"
            try:
                appointment.save()
            except IntegrityError:
                messages.error(request, "That slot was booked by another user.")
                return redirect("slot_list")

            messages.success(request, "Appointment booked successfully.")
            return redirect("my_appointments")
    else:
        form = AppointmentForm()

    return render(
        request,
        "appointments/book.html",
        {"slot": slot, "form": form},
    )


@login_required
def my_appointments(request):
    appointments = (
        Appointment.objects
        .filter(patient=request.user)
        .select_related("slot", "slot__doctor")
        .order_by("slot__date", "slot__start_time")
    )
    return render(
        request,
        "appointments/my_appointments.html",
        {"appointments": appointments},
    )


@login_required
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment.objects.select_related("slot", "slot__doctor"),
        pk=appointment_id,
        patient=request.user,
        status="BOOKED",
    )

    if request.method == "POST":
        form = AppointmentForm(
            request.POST,
            instance=appointment,
            current_appointment=appointment,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated.")
            return redirect("my_appointments")
    else:
        form = AppointmentForm(
            instance=appointment,
            current_appointment=appointment,
        )

    return render(
        request,
        "appointments/edit.html",
        {"appointment": appointment, "form": form},
    )


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        pk=appointment_id,
        patient=request.user,
        status="BOOKED",
    )

    if request.method == "POST":
        appointment.status = "CANCELLED"
        appointment.save(update_fields=["status", "updated_at"])
        messages.success(request, "Appointment cancelled.")
        return redirect("my_appointments")

    return render(
        request,
        "appointments/cancel.html",
        {"appointment": appointment},
    )
