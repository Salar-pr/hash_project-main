from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Attendance, CalendarEvent, HRUser, Schedule, Task


@admin.register(HRUser)
class HRUserAdmin(UserAdmin):
    model = HRUser
    ordering = ("-created_at",)
    list_display = ("username", "role", "is_approved", "is_active", "is_staff", "created_at")
    list_filter = ("role", "is_approved", "is_active", "is_staff")
    search_fields = ("username", "full_name", "email", "department", "job_title")
    readonly_fields = ("hashed", "salt", "signature", "created_at", "updated_at", "last_login")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Profile", {"fields": ("full_name", "email", "phone", "job_title", "department", "salary_ruble")}),
        ("Security hash fields", {"fields": ("hashed", "salt", "signature"), "classes": ("collapse",)}),
        ("Permissions", {"fields": ("role", "is_approved", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Approval", {"fields": ("approved_at", "approved_by")}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "role", "is_approved", "is_staff", "is_superuser"),
            },
        ),
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "work_date", "clock_in", "clock_out", "hours")
    list_filter = ("work_date",)
    search_fields = ("user__username", "user__full_name")


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("user", "week_start", "day_of_week", "shift_start", "shift_end")
    list_filter = ("week_start", "day_of_week")
    search_fields = ("user__username", "user__full_name")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "assigned_to", "status", "priority", "due_date", "created_at")
    list_filter = ("status", "priority", "due_date")
    search_fields = ("title", "assigned_to__username", "assigned_to__full_name")


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "start_at", "end_at", "location")
    list_filter = ("start_at",)
    search_fields = ("title", "user__username", "user__full_name", "location")
