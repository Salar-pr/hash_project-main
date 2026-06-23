from __future__ import annotations

from datetime import datetime, time
from decimal import Decimal

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from al_hash import simple_hash, verify_password


class HRUserManager(BaseUserManager):
    """User manager that keeps the original project hashing algorithm."""

    def create_user(self, username: str, password: str | None = None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        username = self.model.normalize_username(username).strip()
        user = self.model(username=username, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("role", HRUser.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_approved", True)
        return self.create_user(username, password, **extra_fields)


class HRUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model.

    The original project stores three password-security columns:
    hashed, salt, signature. We keep the same approach and do not use
    Django's built-in PBKDF2 password hasher for authentication.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        EMPLOYEE = "employee", "Employee"

    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(blank=True, default="")
    full_name = models.CharField(max_length=200, blank=True, default="")
    phone = models.CharField(max_length=30, blank=True, default="")
    job_title = models.CharField(max_length=100, blank=True, default="")
    department = models.CharField(max_length=100, blank=True, default="")
    salary_ruble = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    hashed = models.BinaryField(null=True, blank=True)
    salt = models.BinaryField(null=True, blank=True)
    signature = models.BinaryField(null=True, blank=True)

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_users",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = HRUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.username

    @property
    def is_admin_role(self) -> bool:
        return self.role == self.Role.ADMIN

    def set_password(self, raw_password: str | None) -> None:
        if raw_password is None:
            self.set_unusable_password()
            return
        hashed, salt, signature = simple_hash(raw_password)
        self.hashed = hashed
        self.salt = salt
        self.signature = signature
        # Keep Django's password column non-sensitive; real verification uses fields above.
        self.password = "al_hash$scrypt_hmac_sha256"

    def check_password(self, raw_password: str) -> bool:
        if not raw_password or not self.salt or not self.signature:
            return False
        return verify_password(raw_password, bytes(self.salt), bytes(self.signature))

    def approve(self, admin_user: "HRUser | None" = None) -> None:
        self.is_approved = True
        self.approved_at = timezone.now()
        if admin_user and admin_user.pk != self.pk:
            self.approved_by = admin_user

    def reject(self) -> None:
        self.is_approved = False
        self.approved_at = None
        self.approved_by = None


class Attendance(models.Model):
    # Keep the original DB column style: attendance.username -> users.username
    user = models.ForeignKey(
        HRUser,
        to_field="username",
        db_column="username",
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    work_date = models.DateField()
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "attendance"
        constraints = [models.UniqueConstraint(fields=["user", "work_date"], name="uq_user_date")]
        ordering = ["-work_date", "user__username"]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.work_date}"

    @property
    def hours(self) -> float:
        if not self.clock_in or not self.clock_out:
            return 0.0
        return round((self.clock_out - self.clock_in).total_seconds() / 3600, 2)


class Schedule(models.Model):
    DAYS = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ]

    # Keep the original DB column style: schedule.username -> users.username
    user = models.ForeignKey(
        HRUser,
        to_field="username",
        db_column="username",
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    week_start = models.DateField()
    day_of_week = models.CharField(max_length=20, choices=DAYS)
    shift_start = models.TimeField()
    shift_end = models.TimeField()

    class Meta:
        db_table = "schedule"
        constraints = [models.UniqueConstraint(fields=["user", "week_start", "day_of_week"], name="uq_sched")]
        ordering = ["week_start", "id"]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.week_start} - {self.day_of_week}"


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To do"
        IN_PROGRESS = "in_progress", "In progress"
        DONE = "done", "Done"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    assigned_to = models.ForeignKey(HRUser, on_delete=models.CASCADE, related_name="tasks")
    created_by = models.ForeignKey(HRUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_tasks")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tasks"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class CalendarEvent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    user = models.ForeignKey(HRUser, on_delete=models.CASCADE, related_name="calendar_events", null=True, blank=True)
    created_by = models.ForeignKey(HRUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_events")
    start_at = models.DateTimeField()
    end_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "calendar_events"
        ordering = ["start_at"]

    def clean(self):
        if self.end_at and self.end_at < self.start_at:
            raise ValidationError("end_at cannot be earlier than start_at")

    def __str__(self) -> str:
        return self.title
