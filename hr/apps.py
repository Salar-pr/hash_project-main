from django.apps import AppConfig


class HrConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hr"
    verbose_name = "HR Portal"

    def ready(self):
        from django.db.models.signals import post_migrate

        from .signals import ensure_default_admin

        post_migrate.connect(ensure_default_admin, sender=self)
