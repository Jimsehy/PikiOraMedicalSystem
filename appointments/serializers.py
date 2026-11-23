from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from .models import Doctor, AppointmentSlot, Appointment

User = get_user_model()


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = "__all__"


class AppointmentSlotSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)
    specialty = serializers.CharField(source="doctor.specialty", read_only=True)
    is_booked = serializers.BooleanField(read_only=True)

    class Meta:
        model = AppointmentSlot
        fields = ["id", "doctor", "doctor_name", "specialty", "date",
                  "start_time", "end_time", "active", "is_booked"]


class AppointmentSerializer(serializers.ModelSerializer):
    patient_username = serializers.CharField(source="patient.username", read_only=True)
    slot_details = AppointmentSlotSerializer(source="slot", read_only=True)
    slot = serializers.PrimaryKeyRelatedField(
        queryset=AppointmentSlot.objects.filter(active=True, doctor__active=True),
        write_only=True, required=False
    )

    class Meta:
        model = Appointment
        fields = ["id", "patient", "patient_username", "slot", "slot_details",
                  "status", "notes", "created_at", "updated_at"]
        read_only_fields = ["id", "patient", "status", "created_at", "updated_at"]

    def validate_slot(self, slot):
        current = self.instance
        if Appointment.objects.filter(slot=slot, status="BOOKED").exclude(
            pk=current.pk if current else None
        ).exists():
            raise serializers.ValidationError("This appointment slot is already booked.")
        return slot

    def create(self, validated_data):
        validated_data["patient"] = self.context["request"].user
        validated_data["status"] = "BOOKED"
        return super().create(validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_active", "is_staff"]
        read_only_fields = ["id", "is_staff"]
