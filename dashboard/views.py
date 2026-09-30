from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from appointments.forms import AppointmentAdminForm, AppointmentSlotForm, DoctorForm
from appointments.models import Appointment, AppointmentSlot, Doctor

User = get_user_model()


def staff_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "Authorised staff access is required.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper


@staff_required
def dashboard_home(request):
    context = {
        "doctor_count": Doctor.objects.count(),
        "slot_count": AppointmentSlot.objects.count(),
        "booking_count": Appointment.objects.filter(status="BOOKED").count(),
        "patient_count": User.objects.filter(is_staff=False).count(),
    }
    return render(request, "dashboard/home.html", context)


@staff_required
def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, "dashboard/doctors/list.html", {"doctors": doctors})


@staff_required
def doctor_create(request):
    form = DoctorForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Doctor added.")
        return redirect("doctor_list")
    return render(request, "dashboard/doctors/form.html", {"form": form, "title": "Add Doctor"})


@staff_required
def doctor_edit(request, doctor_id):
    doctor = get_object_or_404(Doctor, pk=doctor_id)
    form = DoctorForm(request.POST or None, instance=doctor)
    if form.is_valid():
        form.save()
        messages.success(request, "Doctor updated.")
        return redirect("doctor_list")
    return render(request, "dashboard/doctors/form.html", {"form": form, "title": "Edit Doctor"})


@staff_required
def doctor_delete(request, doctor_id):
    doctor = get_object_or_404(Doctor, pk=doctor_id)
    if request.method == "POST":
        doctor.delete()
        messages.success(request, "Doctor deleted.")
        return redirect("doctor_list")
    return render(request, "dashboard/confirm_delete.html", {"object": doctor, "cancel_url": "doctor_list"})


@staff_required
def slot_list_admin(request):
    slots = AppointmentSlot.objects.select_related("doctor").all()
    return render(request, "dashboard/slots/list.html", {"slots": slots})


@staff_required
def slot_create(request):
    form = AppointmentSlotForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Appointment slot created.")
        return redirect("slot_list_admin")
    return render(request, "dashboard/slots/form.html", {"form": form, "title": "Add Appointment Slot"})


@staff_required
def slot_edit(request, slot_id):
    slot = get_object_or_404(AppointmentSlot, pk=slot_id)
    form = AppointmentSlotForm(request.POST or None, instance=slot)
    if form.is_valid():
        form.save()
        messages.success(request, "Appointment slot updated.")
        return redirect("slot_list_admin")
    return render(request, "dashboard/slots/form.html", {"form": form, "title": "Edit Appointment Slot"})


@staff_required
def slot_delete(request, slot_id):
    slot = get_object_or_404(AppointmentSlot, pk=slot_id)
    if request.method == "POST":
        if slot.appointments.filter(status="BOOKED").exists():
            messages.error(request, "Booked slots cannot be deleted.")
            return redirect("slot_list_admin")
        slot.delete()
        messages.success(request, "Appointment slot deleted.")
        return redirect("slot_list_admin")
    return render(request, "dashboard/confirm_delete.html", {"object": slot, "cancel_url": "slot_list_admin"})


@staff_required
def appointment_list_admin(request):
    appointments = Appointment.objects.select_related("patient", "slot", "slot__doctor")
    return render(request, "dashboard/appointments/list.html", {"appointments": appointments})


@staff_required
def appointment_edit_admin(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    form = AppointmentAdminForm(request.POST or None, instance=appointment)
    if form.is_valid():
        form.save()
        messages.success(request, "Appointment updated.")
        return redirect("appointment_list_admin")
    return render(request, "dashboard/appointments/form.html", {"form": form, "title": "Edit Appointment"})


@staff_required
def appointment_delete_admin(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if request.method == "POST":
        appointment.status = "CANCELLED"
        appointment.save(update_fields=["status", "updated_at"])
        messages.success(request, "Appointment cancelled.")
        return redirect("appointment_list_admin")
    return render(request, "dashboard/confirm_delete.html", {"object": appointment, "cancel_url": "appointment_list_admin"})


@staff_required
def patient_list(request):
    patients = User.objects.filter(is_staff=False).order_by("username")
    return render(request, "dashboard/patients/list.html", {"patients": patients})


@staff_required
def toggle_patient(request, user_id):
    patient = get_object_or_404(User, pk=user_id, is_staff=False)
    if request.method == "POST":
        patient.is_active = not patient.is_active
        patient.save(update_fields=["is_active"])
        messages.success(request, "Patient account status updated.")
    return redirect("patient_list")
