from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta

from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView

from .models import Attendance, CalendarEvent, HRUser, Schedule, Task
from .permissions import IsAdminRole, IsApproved
from .serializers import (
    AdminUserSerializer,
    ApprovalAwareTokenRefreshSerializer,
    AttendanceSerializer,
    CalendarEventSerializer,
    EmployeeTaskStatusSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    RegisterSerializer,
    ScheduleSerializer,
    TaskSerializer,
    UserPublicSerializer,
    build_token_bundle,
)


def monday_of(day: date) -> date:
    return day - timedelta(days=day.weekday())


def parse_date_param(value: str | None, default: date | None = None) -> date:
    if not value:
        return default or timezone.localdate()
    return date.fromisoformat(value)


def week_bounds(request) -> tuple[date, date]:
    start = parse_date_param(request.query_params.get("week_start"), monday_of(timezone.localdate()))
    return start, start + timedelta(days=6)


def blacklist_user_jwt_tokens(user: HRUser) -> None:
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)


def serialize_weekly_chart(week_start: date) -> dict:
    week_end = week_start + timedelta(days=6)
    records = (
        Attendance.objects.select_related("user")
        .filter(work_date__gte=week_start, work_date__lte=week_end)
        .order_by("work_date", "user__username")
    )

    by_user_map: dict[int, dict] = {}
    by_day_map = {
        (week_start + timedelta(days=i)).isoformat(): {"date": (week_start + timedelta(days=i)).isoformat(), "hours": 0.0, "records": 0}
        for i in range(7)
    }

    total_hours = 0.0
    for rec in records:
        hours = rec.hours
        total_hours += hours
        user_bucket = by_user_map.setdefault(
            rec.user.pk,
            {
                "user_id": rec.user.pk,
                "username": rec.user.username,
                "full_name": rec.user.full_name,
                "total_hours": 0.0,
                "days": [],
            },
        )
        user_bucket["total_hours"] = round(user_bucket["total_hours"] + hours, 2)
        user_bucket["days"].append(
            {
                "date": rec.work_date.isoformat(),
                "clock_in": timezone.localtime(rec.clock_in).strftime("%H:%M") if rec.clock_in else None,
                "clock_out": timezone.localtime(rec.clock_out).strftime("%H:%M") if rec.clock_out else None,
                "hours": hours,
            }
        )
        day_bucket = by_day_map[rec.work_date.isoformat()]
        day_bucket["hours"] = round(day_bucket["hours"] + hours, 2)
        day_bucket["records"] += 1

    return {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "total_hours": round(total_hours, 2),
        "by_user": list(by_user_map.values()),
        "by_day": list(by_day_map.values()),
    }


# ---------------------------------------------------------------------------
# Auth APIs
# ---------------------------------------------------------------------------


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "status": "pending_approval",
                "message": "Account created. Please wait until admin approves your account.",
                "user": UserPublicSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"].strip()
        password = serializer.validated_data["password"]

        user = HRUser.objects.filter(username__iexact=username).first()
        if not user or not user.check_password(password):
            return Response({"detail": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"detail": "User is inactive."}, status=status.HTTP_403_FORBIDDEN)

        if not user.is_approved:
            return Response(
                {
                    "status": "pending_approval",
                    "detail": "Your account is waiting for admin approval.",
                    "user": UserPublicSerializer(user).data,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        return Response(build_token_bundle(user), status=status.HTTP_200_OK)


class ApprovalAwareTokenRefreshView(TokenRefreshView):
    serializer_class = ApprovalAwareTokenRefreshSerializer


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated, IsApproved]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass
        if request.data.get("delete_token", True):
            Token.objects.filter(user=request.user).delete()
        return Response({"detail": "Logged out."})


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated, IsApproved]

    def get(self, request):
        return Response(UserPublicSerializer(request.user).data)

    def patch(self, request):
        serializer = UserPublicSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # Employees are not allowed to change security/role/approval fields through /me/.
        for blocked in ["role", "is_active", "is_approved", "salary_ruble"]:
            serializer.validated_data.pop(blocked, None)
        serializer.save()
        return Response(UserPublicSerializer(request.user).data)


class PasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated, IsApproved]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data.get("old_password")
        if request.user.role != HRUser.Role.ADMIN and not request.user.check_password(old_password or ""):
            return Response({"detail": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        Token.objects.filter(user=request.user).delete()
        blacklist_user_jwt_tokens(request.user)
        return Response({"detail": "Password changed. Please log in again."})


# ---------------------------------------------------------------------------
# Employee APIs
# ---------------------------------------------------------------------------


class AttendanceSelfAPIView(APIView):
    permission_classes = [IsAuthenticated, IsApproved]

    def get(self, request):
        today = timezone.localdate()
        rec = Attendance.objects.filter(user=request.user, work_date=today).first()
        return Response(AttendanceSerializer(rec).data if rec else None)


class ClockInAPIView(APIView):
    permission_classes = [IsAuthenticated, IsApproved]

    @transaction.atomic
    def post(self, request):
        today = timezone.localdate()
        now = timezone.now()
        rec, _ = Attendance.objects.get_or_create(user=request.user, work_date=today)
        if rec.clock_in:
            return Response(
                {"detail": f"Already clocked in at {timezone.localtime(rec.clock_in).strftime('%H:%M')}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        rec.clock_in = now
        rec.save(update_fields=["clock_in"])
        return Response({"detail": f"Clocked in at {timezone.localtime(now).strftime('%H:%M')}", "record": AttendanceSerializer(rec).data})


class ClockOutAPIView(APIView):
    permission_classes = [IsAuthenticated, IsApproved]

    @transaction.atomic
    def post(self, request):
        today = timezone.localdate()
        now = timezone.now()
        rec = Attendance.objects.filter(user=request.user, work_date=today).first()
        if not rec or not rec.clock_in:
            return Response({"detail": "You have not clocked in today."}, status=status.HTTP_400_BAD_REQUEST)
        if rec.clock_out:
            return Response(
                {"detail": f"Already clocked out at {timezone.localtime(rec.clock_out).strftime('%H:%M')}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        rec.clock_out = now
        rec.save(update_fields=["clock_out"])
        return Response({"detail": f"Clocked out at {timezone.localtime(now).strftime('%H:%M')}", "record": AttendanceSerializer(rec).data})


class MyWeeklyAttendanceAPIView(APIView):
    permission_classes = [IsAuthenticated, IsApproved]

    def get(self, request):
        week_start, week_end = week_bounds(request)
        qs = Attendance.objects.filter(user=request.user, work_date__gte=week_start, work_date__lte=week_end).order_by("work_date")
        total = round(sum(rec.hours for rec in qs), 2)
        return Response(
            {
                "week_start": week_start,
                "week_end": week_end,
                "total_hours": total,
                "records": AttendanceSerializer(qs, many=True).data,
            }
        )


class MyScheduleAPIView(APIView):
    permission_classes = [IsAuthenticated, IsApproved]

    def get(self, request):
        week_start, _ = week_bounds(request)
        qs = Schedule.objects.filter(user=request.user, week_start=week_start).order_by("id")
        return Response({"week_start": week_start, "records": ScheduleSerializer(qs, many=True).data})


class MyTaskViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsApproved]

    def get_queryset(self):
        qs = Task.objects.filter(assigned_to=self.request.user).order_by("-created_at")
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    @action(detail=True, methods=["patch"], serializer_class=EmployeeTaskStatusSerializer)
    def status(self, request, pk=None):
        task = self.get_object()
        serializer = EmployeeTaskStatusSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TaskSerializer(task).data)


class MyCalendarEventViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated, IsApproved]

    def get_queryset(self):
        qs = CalendarEvent.objects.filter(Q(user=self.request.user) | Q(user__isnull=True)).order_by("start_at")
        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")
        if start:
            qs = qs.filter(start_at__date__gte=parse_date_param(start))
        if end:
            qs = qs.filter(start_at__date__lte=parse_date_param(end))
        return qs


# ---------------------------------------------------------------------------
# Custom Admin Panel APIs - separate from Django admin
# ---------------------------------------------------------------------------


class AdminDashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        today = timezone.localdate()
        week_start = monday_of(today)
        week_end = week_start + timedelta(days=6)
        return Response(
            {
                "members_total": HRUser.objects.count(),
                "members_active": HRUser.objects.filter(is_active=True).count(),
                "members_pending_approval": HRUser.objects.filter(is_approved=False, is_active=True).count(),
                "admins_total": HRUser.objects.filter(role=HRUser.Role.ADMIN).count(),
                "attendance_today": Attendance.objects.filter(work_date=today).count(),
                "tasks_open": Task.objects.exclude(status__in=[Task.Status.DONE, Task.Status.CANCELLED]).count(),
                "tasks_done": Task.objects.filter(status=Task.Status.DONE).count(),
                "events_this_week": CalendarEvent.objects.filter(start_at__date__gte=week_start, start_at__date__lte=week_end).count(),
                "weekly_chart": serialize_weekly_chart(week_start),
            }
        )


class AdminWeeklyChartAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        week_start, _ = week_bounds(request)
        return Response(serialize_weekly_chart(week_start))


class AdminUserViewSet(viewsets.ModelViewSet):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        qs = HRUser.objects.select_related("approved_by").all()
        role = self.request.query_params.get("role")
        approved = self.request.query_params.get("approved")
        search = self.request.query_params.get("search")
        if role:
            qs = qs.filter(role=role)
        if approved is not None:
            qs = qs.filter(is_approved=approved.lower() in ["1", "true", "yes"])
        if search:
            qs = qs.filter(
                Q(username__icontains=search)
                | Q(full_name__icontains=search)
                | Q(email__icontains=search)
                | Q(department__icontains=search)
                | Q(job_title__icontains=search)
            )
        return qs.order_by("-created_at")

    def perform_update(self, serializer):
        before = self.get_object()
        was_active = before.is_active
        was_approved = before.is_approved
        user = serializer.save()
        if (was_active and not user.is_active) or (was_approved and not user.is_approved):
            Token.objects.filter(user=user).delete()
            blacklist_user_jwt_tokens(user)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        user = self.get_object()
        user.approve(request.user)
        user.is_active = True
        user.save(update_fields=["is_approved", "approved_at", "approved_by", "is_active"])
        return Response({"detail": "User approved.", "user": AdminUserSerializer(user).data})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        user = self.get_object()
        if user.pk == request.user.pk:
            return Response({"detail": "You cannot reject yourself."}, status=status.HTTP_400_BAD_REQUEST)
        user.reject()
        user.save(update_fields=["is_approved", "approved_at", "approved_by"])
        Token.objects.filter(user=user).delete()
        blacklist_user_jwt_tokens(user)
        return Response({"detail": "User moved to pending/rejected state.", "user": AdminUserSerializer(user).data})

    @action(detail=True, methods=["post"], url_path="set-password")
    def set_password_action(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordChangeSerializer(data={"new_password": request.data.get("password")})
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        Token.objects.filter(user=user).delete()
        blacklist_user_jwt_tokens(user)
        return Response({"detail": "Password updated."})

    @action(detail=True, methods=["get"], url_path="full-info")
    def full_info(self, request, pk=None):
        user = self.get_object()
        week_start, week_end = week_bounds(request)
        attendance = Attendance.objects.filter(user=user, work_date__gte=week_start, work_date__lte=week_end).order_by("work_date")
        schedules = Schedule.objects.filter(user=user, week_start=week_start).order_by("id")
        tasks = Task.objects.filter(assigned_to=user).order_by("-created_at")
        events = CalendarEvent.objects.filter(Q(user=user) | Q(user__isnull=True), start_at__date__gte=week_start, start_at__date__lte=week_end)
        return Response(
            {
                "user": AdminUserSerializer(user).data,
                "week_start": week_start,
                "week_end": week_end,
                "attendance_total_hours": round(sum(a.hours for a in attendance), 2),
                "attendance": AttendanceSerializer(attendance, many=True).data,
                "schedule": ScheduleSerializer(schedules, many=True).data,
                "tasks": TaskSerializer(tasks, many=True).data,
                "calendar_events": CalendarEventSerializer(events, many=True).data,
            }
        )


class AdminAttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        qs = Attendance.objects.select_related("user").all()
        user_id = self.request.query_params.get("user")
        username = self.request.query_params.get("username")
        if user_id:
            qs = qs.filter(user__id=user_id)
        if username:
            qs = qs.filter(user__username__iexact=username)
        if self.request.query_params.get("week_start"):
            week_start, week_end = week_bounds(self.request)
            qs = qs.filter(work_date__gte=week_start, work_date__lte=week_end)
        else:
            start = self.request.query_params.get("start")
            end = self.request.query_params.get("end")
            if start:
                qs = qs.filter(work_date__gte=parse_date_param(start))
            if end:
                qs = qs.filter(work_date__lte=parse_date_param(end))
        return qs.order_by("-work_date", "user__username")


class AdminScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        qs = Schedule.objects.select_related("user").all()
        user_id = self.request.query_params.get("user")
        username = self.request.query_params.get("username")
        week_start = self.request.query_params.get("week_start")
        if user_id:
            qs = qs.filter(user__id=user_id)
        if username:
            qs = qs.filter(user__username__iexact=username)
        if week_start:
            qs = qs.filter(week_start=parse_date_param(week_start))
        return qs.order_by("week_start", "id")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        obj, _created = Schedule.objects.update_or_create(
            user=data["user"],
            week_start=data["week_start"],
            day_of_week=data["day_of_week"],
            defaults={"shift_start": data["shift_start"], "shift_end": data["shift_end"]},
        )
        return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)


class AdminTaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        qs = Task.objects.select_related("assigned_to", "created_by").all()
        assigned_to = self.request.query_params.get("assigned_to")
        status_param = self.request.query_params.get("status")
        due = self.request.query_params.get("due_date")
        if assigned_to:
            qs = qs.filter(assigned_to_id=assigned_to)
        if status_param:
            qs = qs.filter(status=status_param)
        if due:
            qs = qs.filter(due_date=parse_date_param(due))
        return qs.order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AdminCalendarEventViewSet(viewsets.ModelViewSet):
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        qs = CalendarEvent.objects.select_related("user", "created_by").all()
        user_id = self.request.query_params.get("user")
        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")
        if user_id:
            qs = qs.filter(Q(user_id=user_id) | Q(user__isnull=True))
        if start:
            qs = qs.filter(start_at__date__gte=parse_date_param(start))
        if end:
            qs = qs.filter(start_at__date__lte=parse_date_param(end))
        return qs.order_by("start_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
