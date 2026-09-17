from django.urls import path
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

from .views import (
    HealthCheckView,
    RegisterView,
    CurrentUserView,
    MyTokenObtainPairView,
    LogoutView,
    VerifyEmailView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

app_name = "accounts"


class PublicTokenBlacklistView(TokenBlacklistView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def handle_exception(self, exc):
        return Response({"detail": "Logout completed."}, status=status.HTTP_200_OK)

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("login/", MyTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/blacklist/", PublicTokenBlacklistView.as_view(), name="token-blacklist"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", CurrentUserView.as_view(), name="me"),
]
