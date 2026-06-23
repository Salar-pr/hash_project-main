from __future__ import annotations

from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Attendance, CalendarEvent, HRUser, Schedule, Task


class UserPublicSerializer(serializers.ModelSerializer):
    approved_by_username = serializers.CharField(source="approved_by.username", read_only=True)

    class Meta:
        model = HRUser
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "phone",
            "job_title",
            "department",
            "salary_ruble",
            "role",
            "is_active",
            "is_approved",
            "approved_at",
            "approved_by_username",
            "created_at",
            "updated_at",
            "last_login",
        ]
        read_only_fields = ["id", "approved_at", "approved_by_username", "created_at", "updated_at", "last_login"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = HRUser
        fields = [
            "username",
            "password",
            "password_confirm",
            "email",
            "full_name",
            "phone",
            "job_title",
            "department",
        ]

    def validate_username(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Username is required.")
        if HRUser.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = HRUser(**validated_data)
        user.role = HRUser.Role.EMPLOYEE
        user.is_staff = False
        user.is_superuser = False
        user.is_active = True
        user.is_approved = False
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class ApprovalAwareTokenRefreshSerializer(TokenRefreshSerializer):
    """Refresh JWT only if the user is still active and admin-approved."""

    def validate(self, attrs):
        refresh = RefreshToken(attrs["refresh"])
        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM)
        user = HRUser.objects.filter(pk=user_id).first()
        if not user or not user.is_active:
            raise serializers.ValidationError({"detail": "User is inactive."})
        if not user.is_approved:
            raise serializers.ValidationError({"detail": "User is waiting for admin approval."})
        return super().validate(attrs)


class TokenBundleSerializer(serializers.Serializer):
    user = UserPublicSerializer()
    access = serializers.CharField()
    refresh = serializers.CharField()
    token = serializers.CharField(help_text="DRF TokenAuthentication token")
    token_type = serializers.CharField(default="Bearer")


def build_token_bundle(user: HRUser) -> dict:
    refresh = RefreshToken.for_user(user)
    token, _ = Token.objects.get_or_create(user=user)
    return {
        "user": UserPublicSerializer(user).data,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "token": token.key,
        "token_type": "Bearer",
    }


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=False, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, min_length=6, trim_whitespace=False)


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=6, trim_whitespace=False)
    approved_by_username = serializers.CharField(source="approved_by.username", read_only=True)

    class Meta:
        model = HRUser
        fields = [
            "id",
            "username",
            "password",
            "email",
            "full_name",
            "phone",
            "job_title",
            "department",
            "salary_ruble",
            "role",
            "is_active",
            "is_staff",
            "is_approved",
            "approved_at",
            "approved_by",
            "approved_by_username",
            "created_at",
            "updated_at",
            "last_login",
        ]
        read_only_fields = ["id", "approved_at", "approved_by_username", "created_at", "updated_at", "last_login"]
        extra_kwargs = {"approved_by": {"required": False, "allow_null": True}}

    def validate_username(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Username is required.")
        qs = HRUser.objects.filter(username__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password", None) or "12345678"
        role = validated_data.get("role", HRUser.Role.EMPLOYEE)
        validated_data.setdefault("is_approved", True)
        validated_data.setdefault("is_active", True)
        validated_data.setdefault("is_staff", role == HRUser.Role.ADMIN)
        user = HRUser(**validated_data)
        user.set_password(password)
        if user.is_approved and not user.approved_at:
            request = self.context.get("request")
            user.approve(request.user if request and request.user.is_authenticated else None)
        user.save()
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password:
            instance.set_password(password)
        if instance.role == HRUser.Role.ADMIN:
            instance.is_staff = True
        instance.save()
        return instance


class AttendanceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=HRUser.objects.all())
    username = serializers.CharField(source="user.username", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)
    hours = serializers.FloatField(read_only=True)

    class Meta:
        model = Attendance
        fields = ["id", "user", "username", "user_full_name", "work_date", "clock_in", "clock_out", "hours"]
        read_only_fields = ["id", "username", "user_full_name", "hours"]


class ScheduleSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=HRUser.objects.all())
    username = serializers.CharField(source="user.username", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Schedule
        fields = [
            "id",
            "user",
            "username",
            "user_full_name",
            "week_start",
            "day_of_week",
            "shift_start",
            "shift_end",
        ]
        read_only_fields = ["id", "username", "user_full_name"]


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_username = serializers.CharField(source="assigned_to.username", read_only=True)
    assigned_to_full_name = serializers.CharField(source="assigned_to.full_name", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "assigned_to",
            "assigned_to_username",
            "assigned_to_full_name",
            "created_by",
            "created_by_username",
            "status",
            "priority",
            "due_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_by_username", "created_at", "updated_at"]


class EmployeeTaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["status"]


class CalendarEventSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = CalendarEvent
        fields = [
            "id",
            "title",
            "description",
            "user",
            "username",
            "user_full_name",
            "created_by",
            "created_by_username",
            "start_at",
            "end_at",
            "location",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_by_username", "created_at", "updated_at"]


class WeeklyChartSerializer(serializers.Serializer):
    week_start = serializers.DateField()
    week_end = serializers.DateField()
    total_hours = serializers.FloatField()
    by_user = serializers.ListField()
    by_day = serializers.ListField()
