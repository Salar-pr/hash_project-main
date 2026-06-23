# Generated manually for the DRF backend conversion.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="HRUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("username", models.CharField(db_index=True, max_length=150, unique=True)),
                ("email", models.EmailField(blank=True, default="", max_length=254)),
                ("full_name", models.CharField(blank=True, default="", max_length=200)),
                ("phone", models.CharField(blank=True, default="", max_length=30)),
                ("job_title", models.CharField(blank=True, default="", max_length=100)),
                ("department", models.CharField(blank=True, default="", max_length=100)),
                ("salary_ruble", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("hashed", models.BinaryField(blank=True, null=True)),
                ("salt", models.BinaryField(blank=True, null=True)),
                ("signature", models.BinaryField(blank=True, null=True)),
                ("role", models.CharField(choices=[("admin", "Admin"), ("employee", "Employee")], default="employee", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_approved", models.BooleanField(default=False)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("approved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="approved_users", to=settings.AUTH_USER_MODEL)),
                ("groups", models.ManyToManyField(blank=True, help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.", related_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups")),
                ("user_permissions", models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="user_set", related_query_name="user", to="auth.permission", verbose_name="user permissions")),
            ],
            options={
                "db_table": "users",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Attendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("work_date", models.DateField()),
                ("clock_in", models.DateTimeField(blank=True, null=True)),
                ("clock_out", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(db_column="username", on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to=settings.AUTH_USER_MODEL, to_field="username")),
            ],
            options={
                "db_table": "attendance",
                "ordering": ["-work_date", "user__username"],
            },
        ),
        migrations.CreateModel(
            name="CalendarEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("start_at", models.DateTimeField()),
                ("end_at", models.DateTimeField(blank=True, null=True)),
                ("location", models.CharField(blank=True, default="", max_length=200)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_events", to=settings.AUTH_USER_MODEL)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="calendar_events", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "calendar_events",
                "ordering": ["start_at"],
            },
        ),
        migrations.CreateModel(
            name="Schedule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("week_start", models.DateField()),
                ("day_of_week", models.CharField(choices=[("Monday", "Monday"), ("Tuesday", "Tuesday"), ("Wednesday", "Wednesday"), ("Thursday", "Thursday"), ("Friday", "Friday"), ("Saturday", "Saturday"), ("Sunday", "Sunday")], max_length=20)),
                ("shift_start", models.TimeField()),
                ("shift_end", models.TimeField()),
                ("user", models.ForeignKey(db_column="username", on_delete=django.db.models.deletion.CASCADE, related_name="schedules", to=settings.AUTH_USER_MODEL, to_field="username")),
            ],
            options={
                "db_table": "schedule",
                "ordering": ["week_start", "id"],
            },
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("status", models.CharField(choices=[("todo", "To do"), ("in_progress", "In progress"), ("done", "Done"), ("cancelled", "Cancelled")], default="todo", max_length=20)),
                ("priority", models.CharField(choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("urgent", "Urgent")], default="medium", max_length=20)),
                ("due_date", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("assigned_to", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tasks", to=settings.AUTH_USER_MODEL)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_tasks", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "tasks",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="attendance",
            constraint=models.UniqueConstraint(fields=("user", "work_date"), name="uq_user_date"),
        ),
        migrations.AddConstraint(
            model_name="schedule",
            constraint=models.UniqueConstraint(fields=("user", "week_start", "day_of_week"), name="uq_sched"),
        ),
    ]
