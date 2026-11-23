from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .models import Doctor, AppointmentSlot, Appointment
from .serializers import (
    DoctorSerializer, AppointmentSlotSerializer, AppointmentSerializer,
    RegisterSerializer, PatientSerializer,
)

User = get_user_model()


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": {
            "id": user.id, "username": user.username, "email": user.email
        }}, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = authenticate(
            request, username=request.data.get("username"),
            password=request.data.get("password")
        )
        if user is None:
            return Response({"detail": "Invalid username or password."},
                            status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({"detail": "This account is inactive."},
                            status=status.HTTP_403_FORBIDDEN)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": {
            "id": user.id, "username": user.username, "email": user.email,
            "is_staff": user.is_staff
        }})


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_permissions(self):
        return [AllowAny()] if self.action == "list" or self.action == "retrieve" else [IsAdminUser()]

    def get_queryset(self):
        qs = Doctor.objects.all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(active=True)
        return qs


class AppointmentSlotViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSlotSerializer

    def get_queryset(self):
        qs = AppointmentSlot.objects.select_related("doctor").all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(active=True, doctor__active=True, date__gte=timezone.localdate())
        return qs

    def get_permissions(self):
        return [AllowAny()] if self.action in ["list", "retrieve"] else [IsAdminUser()]


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Appointment.objects.select_related(
            "patient", "slot", "slot__doctor"
        )
        if self.request.user.is_staff:
            return qs
        return qs.filter(patient=self.request.user)

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                serializer.save(patient=self.request.user, status="BOOKED")
        except IntegrityError:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"slot": "This appointment slot has already been booked."})

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_staff and instance.patient_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not request.user.is_staff and instance.status != "BOOKED":
            return Response({"detail": "Only booked appointments can be edited."},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if not request.user.is_staff and appointment.patient_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        appointment.status = "CANCELLED"
        appointment.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(appointment).data)


class PatientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_staff=False).order_by("username")
    serializer_class = PatientSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        patient = self.get_object()
        patient.is_active = not patient.is_active
        patient.save(update_fields=["is_active"])
        return Response(self.get_serializer(patient).data)


class AdminSummaryAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({
            "doctor_count": Doctor.objects.count(),
            "slot_count": AppointmentSlot.objects.count(),
            "booking_count": Appointment.objects.filter(status="BOOKED").count(),
            "patient_count": User.objects.filter(is_staff=False).count(),
        })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_api(request):
    request.user.auth_token.delete()
    return Response({"detail": "Logged out successfully."})
