from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Appointment, AppointmentSlot, Doctor


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ("slot", "notes")
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Optional notes"}),
        }

    def __init__(self, *args, **kwargs):
        current_appointment = kwargs.pop("current_appointment", None)
        super().__init__(*args, **kwargs)
        if current_appointment:
            self.fields["slot"].queryset = (
                AppointmentSlot.objects
                .filter(active=True, doctor__active=True)
                .exclude(appointments__status="BOOKED")
                .select_related("doctor")
                | AppointmentSlot.objects.filter(pk=current_appointment.slot_id)
            ).distinct().order_by("date", "start_time")
        else:
            self.fields["slot"].queryset = (
                AppointmentSlot.objects
                .filter(active=True, doctor__active=True)
                .exclude(appointments__status="BOOKED")
                .select_related("doctor")
                .order_by("date", "start_time")
            )

    def clean_slot(self):
        slot = self.cleaned_data["slot"]
        if Appointment.objects.filter(slot=slot, status="BOOKED").exclude(
            pk=self.instance.pk
        ).exists():
            raise forms.ValidationError("That appointment slot is already booked.")
        return slot


class AppointmentSlotForm(forms.ModelForm):
    class Meta:
        model = AppointmentSlot
        fields = ("doctor", "date", "start_time", "end_time", "active")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")
        if start and end and end <= start:
            raise forms.ValidationError("End time must be after start time.")
        return cleaned


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ("name", "specialty", "email", "phone", "bio", "active")


class AppointmentAdminForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ("patient", "slot", "status", "notes")
