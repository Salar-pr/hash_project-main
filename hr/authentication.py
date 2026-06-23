from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class ApprovalMixin:
    def _enforce_approval(self, user):
        if not user or not user.is_active:
            raise AuthenticationFailed("User is inactive.")
        if not getattr(user, "is_approved", False):
            raise AuthenticationFailed("User is waiting for admin approval.")
        return user


class ApprovalAwareJWTAuthentication(ApprovalMixin, JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None
        user, token = result
        return self._enforce_approval(user), token


class ApprovalAwareTokenAuthentication(ApprovalMixin, TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        return self._enforce_approval(user), token
