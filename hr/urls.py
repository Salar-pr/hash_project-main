from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView

from .views import (
    AdminAttendanceViewSet,
    AdminCalendarEventViewSet,
    AdminDashboardStatsAPIView,
    AdminScheduleViewSet,
    AdminTaskViewSet,
    AdminUserViewSet,
    AdminWeeklyChartAPIView,
    ApprovalAwareTokenRefreshView,
    AttendanceSelfAPIView,
    ClockInAPIView,
    ClockOutAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    MyCalendarEventViewSet,
    MyScheduleAPIView,
    MyTaskViewSet,
    MyWeeklyAttendanceAPIView,
    PasswordChangeAPIView,
    RegisterAPIView,
)

employee_router = DefaultRouter()
employee_router.register(r"tasks", MyTaskViewSet, basename="my-tasks")
employee_router.register(r"calendar", MyCalendarEventViewSet, basename="my-calendar")

admin_router = DefaultRouter()
admin_router.register(r"members", AdminUserViewSet, basename="admin-members")
admin_router.register(r"attendance", AdminAttendanceViewSet, basename="admin-attendance")
admin_router.register(r"schedules", AdminScheduleViewSet, basename="admin-schedules")
admin_router.register(r"tasks", AdminTaskViewSet, basename="admin-tasks")
admin_router.register(r"calendar-events", AdminCalendarEventViewSet, basename="admin-calendar-events")

urlpatterns = [
    # Auth: both JWT and DRF token are issued by /auth/login/.
    path("auth/register/", RegisterAPIView.as_view(), name="auth-register"),
    path("auth/login/", LoginAPIView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutAPIView.as_view(), name="auth-logout"),
    path("auth/me/", MeAPIView.as_view(), name="auth-me"),
    path("auth/change-password/", PasswordChangeAPIView.as_view(), name="auth-change-password"),
    path("auth/jwt/refresh/", ApprovalAwareTokenRefreshView.as_view(), name="jwt-refresh"),
    path("auth/jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),

    # Employee web-app APIs.
    path("attendance/today/", AttendanceSelfAPIView.as_view(), name="attendance-today"),
    path("attendance/clock-in/", ClockInAPIView.as_view(), name="attendance-clock-in"),
    path("attendance/clock-out/", ClockOutAPIView.as_view(), name="attendance-clock-out"),
    path("attendance/weekly/", MyWeeklyAttendanceAPIView.as_view(), name="attendance-weekly"),
    path("schedules/my/", MyScheduleAPIView.as_view(), name="my-schedule"),
    path("", include(employee_router.urls)),

    # Custom admin-panel APIs, intentionally separate from /django-admin/.
    path("admin-panel/dashboard/stats/", AdminDashboardStatsAPIView.as_view(), name="admin-dashboard-stats"),
    path("admin-panel/charts/weekly/", AdminWeeklyChartAPIView.as_view(), name="admin-weekly-chart"),
    path("admin-panel/", include(admin_router.urls)),
]
