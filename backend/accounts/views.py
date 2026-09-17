from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
    ParticipantProfileSerializer,
)
from .models import ParticipantProfile
from .recovery import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    VerifyEmailSerializer,
    send_verification_email,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_verification_email(user)
        return Response(serializer.to_representation(user), status=status.HTTP_201_CREATED)


class VerifyEmailView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Email verified successfully."})


class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "If an account exists, reset instructions have been sent."})


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password reset successfully."})


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response is not None and response.status_code == status.HTTP_400_BAD_REQUEST:
            response.status_code = status.HTTP_401_UNAUTHORIZED
        return response


class LogoutView(TokenBlacklistView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
        except (TokenError, APIException):
            return Response({"detail": "Logout completed."}, status=status.HTTP_200_OK)
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            return Response({"detail": "Logout completed."}, status=status.HTTP_200_OK)
        return response

    def handle_exception(self, exc):
        return Response({"detail": "Logout completed."}, status=status.HTTP_200_OK)


class CurrentUserView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        return Response(self.get_serializer(user).data)

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        user_serializer = UserSerializer(user, data=request.data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        profile_data = request.data.get("profile")
        if profile_data is None:
            profile_data = request.data.get("participantprofile")
        if profile_data is not None and isinstance(profile_data, dict):
            profile = user.profile
            profile_serializer = ParticipantProfileSerializer(
                profile, data=profile_data, partial=True
            )
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()
        return Response(UserSerializer(user).data)


class HealthCheckView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        return Response({"status": "ok", "app": "accounts"}, status=status.HTTP_200_OK)
