from __future__ import annotations

from django.db import OperationalError, ProgrammingError
from django.utils import timezone


def ensure_default_admin(sender, **kwargs):
    """Create/update the requested custom admin account after migrations."""
    try:
        from .models import HRUser

        user, created = HRUser.objects.get_or_create(username="salar")
        changed_fields: list[str] = []

        if created or not user.check_password("12345678"):
            user.set_password("12345678")
            changed_fields.extend(["password", "hashed", "salt", "signature"])

        defaults = {
            "role": HRUser.Role.ADMIN,
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
            "is_approved": True,
        }
        for field, value in defaults.items():
            if getattr(user, field) != value:
                setattr(user, field, value)
                changed_fields.append(field)

        if not user.approved_at:
            user.approved_at = timezone.now()
            changed_fields.append("approved_at")

        if changed_fields:
            user.save(update_fields=list(set(changed_fields + ["updated_at"])))
    except (OperationalError, ProgrammingError):
        # Tables may not exist yet in early migration/setup commands.
        return
