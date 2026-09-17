from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, dumps, loads
from django.utils.encoding import force_str
from rest_framework import serializers

from .models import ParticipantProfile

User = get_user_model()


def verification_token(user):
    return dumps({"user_id": user.id}, salt="kpitb-email-verification")


def send_verification_email(user):
    token = verification_token(user)
    send_mail(
        "Verify your KPITB Hackathon account",
        f"Use this verification token to activate your account: {token}",
        None,
        [user.email],
        fail_silently=False,
    )
    return token


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()

    def save(self):
        try:
            payload = loads(self.validated_data["token"], salt="kpitb-email-verification", max_age=60 * 60 * 24 * 3)
        except (BadSignature, SignatureExpired):
            raise serializers.ValidationError({"token": "This verification token is invalid or expired."})
        try:
            user = User.objects.get(id=payload["user_id"])
        except (User.DoesNotExist, KeyError):
            raise serializers.ValidationError({"token": "This verification token is invalid."})
        profile, _ = ParticipantProfile.objects.get_or_create(user=user)
        profile.is_verified = True
        profile.save(update_fields=["is_verified", "updated_at"])
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self):
        user = User.objects.filter(email__iexact=self.validated_data["email"], is_active=True).first()
        if user:
            token = default_token_generator.make_token(user)
            send_mail(
                "Reset your KPITB Hackathon password",
                f"Use this reset token with your user id {user.id}: {token}",
                None,
                [user.email],
                fail_silently=False,
            )
        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirmation = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirmation"]:
            raise serializers.ValidationError({"new_password_confirmation": "Passwords do not match."})
        try:
            user = User.objects.get(id=attrs["user_id"], is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_id": "Invalid password reset request."})
        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError({"token": "This reset token is invalid or expired."})
        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user
