from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsApproved(BasePermission):
    message = "Your account is waiting for admin approval."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.is_active and user.is_approved)


class IsAdminRole(BasePermission):
    message = "Admin role is required."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and user.is_approved
            and getattr(user, "role", None) == "admin"
        )


class IsOwnerReadOnlyOrAdmin(BasePermission):
    """Admins can do everything; employees can only read their own object."""

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if getattr(user, "role", None) == "admin":
            return True
        target_user = getattr(obj, "user", None) or getattr(obj, "assigned_to", None)
        return request.method in SAFE_METHODS and target_user == user
