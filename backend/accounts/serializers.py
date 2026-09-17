from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import ParticipantProfile

User = get_user_model()


class ParticipantProfileSerializer(serializers.ModelSerializer):
    is_complete = serializers.BooleanField(read_only=True)

    class Meta:
        model = ParticipantProfile
        fields = (
            "id",
            "phone",
            "institution",
            "district",
            "education_level",
            "skills",
            "bio",
            "portfolio_url",
            "github_url",
            "is_judge",
            "is_verified",
            "is_complete",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "is_judge", "is_verified")


class UserSerializer(serializers.ModelSerializer):
    profile = ParticipantProfileSerializer(read_only=True)
    participantprofile = ParticipantProfileSerializer(source="profile", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "date_joined",
            "profile",
            "participantprofile",
        )
        read_only_fields = (
            "id",
            "is_staff",
            "is_active",
            "date_joined",
            "email",
        )


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    institution = serializers.CharField(required=False, allow_blank=True)
    district = serializers.CharField(required=False, allow_blank=True)
    education_level = serializers.CharField(required=False, allow_blank=True)
    skills = serializers.ListField(
        child=serializers.CharField(max_length=80), required=False, allow_empty=True
    )
    bio = serializers.CharField(required=False, allow_blank=True)
    portfolio_url = serializers.URLField(required=False, allow_blank=True)
    github_url = serializers.URLField(required=False, allow_blank=True)
    is_judge = serializers.BooleanField(required=False, default=False)
    participantprofile = ParticipantProfileSerializer(required=False, write_only=True)

    def validate_email(self, value: str) -> str:
        email = value.lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.", code="DUPLICATE_EMAIL"
            )
        return email

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Passwords do not match."}, code="PASSWORDS_MISMATCH"
            )
        try:
            validate_password(attrs["password1"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                {"password1": list(exc.messages)}, code="WEAK_PASSWORD"
            )
        return attrs

    def create(self, validated_data):
        email = validated_data["email"].lower().strip()
        participantprofile = validated_data.pop("participantprofile", {})
        username_base = slugify(email.split("@")[0]) or email
        base = username_base
        counter = 1
        username = base
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1
        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data["password1"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        profile = user.profile
        profile.phone = validated_data.get("phone", participantprofile.get("phone")) or None
        profile.institution = validated_data.get(
            "institution", participantprofile.get("institution")
        ) or None
        profile.district = validated_data.get(
            "district", participantprofile.get("district")
        ) or None
        profile.education_level = validated_data.get(
            "education_level", participantprofile.get("education_level")
        ) or None
        profile.skills = validated_data.get(
            "skills", participantprofile.get("skills", [])
        )
        profile.bio = validated_data.get(
            "bio", participantprofile.get("bio", "")
        )
        profile.portfolio_url = validated_data.get(
            "portfolio_url", participantprofile.get("portfolio_url")
        ) or None
        profile.github_url = validated_data.get(
            "github_url", participantprofile.get("github_url")
        ) or None
        # Judge access is organizer-controlled; public registration cannot grant it.
        profile.is_judge = False
        profile.save(update_fields=[
            "phone", "institution", "district", "education_level", "skills",
            "bio", "portfolio_url", "github_url", "is_judge", "updated_at"
        ])
        return user

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "email": instance.email,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "profile_id": instance.profile.id,
            "participantprofile": ParticipantProfileSerializer(instance.profile).data,
        }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    def validate(self, attrs):
        email = (attrs.get("email") or attrs.get("username") or "").lower().strip()
        password = attrs.get("password", "")
        if not email or not password:
            raise serializers.ValidationError(
                "Email and password are required.", code="MISSING_CREDENTIALS"
            )
        user = User.objects.filter(email__iexact=email).first()
        if user is None or not user.check_password(password):
            raise serializers.ValidationError(
                "No active account found with the given credentials.",
                code="INVALID_CREDENTIALS",
            )
        if not user.is_active:
            raise serializers.ValidationError(
                "Account is disabled.", code="INACTIVE_ACCOUNT"
            )
        refresh = self.get_token(user)
        data = {}
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data
