from django.utils import timezone
from rest_framework import serializers
from .models import (
    Hackathon, ProblemStatement, ParticipantEnrollment,
    JudgingCriterion, HackathonRegistration,
)


class HackathonListSerializer(serializers.ModelSerializer):
    is_registration_open = serializers.BooleanField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    problem_count = serializers.IntegerField(read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    team_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Hackathon
        fields = (
            "id",
            "title",
            "slug",
            "tagline",
            "cover_image_url",
            "starts_at",
            "ends_at",
            "registration_opens_at",
            "registration_closes_at",
            "team_min_size",
            "team_max_size",
            "is_active",
            "is_registration_open",
            "is_ongoing",
            "is_completed",
            "tracks",
            "problem_count",
            "participant_count",
            "team_count",
        )


class HackathonSerializer(serializers.ModelSerializer):
    starts_at = serializers.DateTimeField(required=False)
    ends_at = serializers.DateTimeField(required=False)
    registration_opens_at = serializers.DateTimeField(required=False)
    registration_closes_at = serializers.DateTimeField(required=False)
    start_date = serializers.DateTimeField(write_only=True, required=False)
    end_date = serializers.DateTimeField(write_only=True, required=False)
    registration_start = serializers.DateTimeField(write_only=True, required=False)
    registration_end = serializers.DateTimeField(write_only=True, required=False)
    prizes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    is_registration_open = serializers.BooleanField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    judging_criteria_count = serializers.IntegerField(read_only=True)
    problem_count = serializers.IntegerField(read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    team_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Hackathon
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "judging_criteria_count")

    def validate(self, attrs):
        aliases = {
            "start_date": "starts_at",
            "end_date": "ends_at",
            "registration_start": "registration_opens_at",
            "registration_end": "registration_closes_at",
            "prizes": "prizes_text",
        }
        for alias, field in aliases.items():
            if field not in attrs and alias in attrs:
                attrs[field] = attrs[alias]
        for alias in aliases:
            attrs.pop(alias, None)

        if attrs.get("registration_opens_at") and attrs.get("registration_closes_at"):
            if attrs["registration_opens_at"] >= attrs["registration_closes_at"]:
                raise serializers.ValidationError(
                    "Registration opens must be before registration closes."
                )
        if attrs.get("starts_at") and attrs.get("ends_at"):
            if attrs["starts_at"] >= attrs["ends_at"]:
                raise serializers.ValidationError(
                    "Hackathon start must be before end."
                )
        if attrs.get("team_min_size") and attrs.get("team_max_size"):
            if attrs["team_min_size"] > attrs["team_max_size"]:
                raise serializers.ValidationError(
                    "team_min_size cannot exceed team_max_size."
                )
        return attrs


class JudgingCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JudgingCriterion
        fields = "__all__"
        read_only_fields = ("created_at",)


class ProblemStatementSerializer(serializers.ModelSerializer):
    hackathon_title = serializers.CharField(source="hackathon.title", read_only=True)
    hackathon_slug = serializers.CharField(source="hackathon.slug", read_only=True)

    class Meta:
        model = ProblemStatement
        fields = (
            "id", "hackathon", "hackathon_title", "hackathon_slug", "title", "slug",
            "category", "summary", "description", "deliverables", "difficulty",
            "is_published", "created_at", "updated_at"
        )
        read_only_fields = ("slug", "created_at", "updated_at")


class ParticipantEnrollmentSerializer(serializers.ModelSerializer):
    hackathon_title = serializers.CharField(source="hackathon.title", read_only=True)
    hackathon_slug = serializers.CharField(source="hackathon.slug", read_only=True)
    selected_problem_title = serializers.CharField(source="selected_problem.title", read_only=True)
    participant_name = serializers.SerializerMethodField()
    participant_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = ParticipantEnrollment
        fields = (
            "id", "hackathon", "hackathon_title", "hackathon_slug", "user",
            "participant_name", "participant_email", "selected_problem",
            "selected_problem_title", "participation_preference", "primary_role",
            "experience_level", "attendance_mode", "motivation", "agreed_to_rules",
            "status", "created_at", "updated_at"
        )
        read_only_fields = (
            "hackathon", "user", "status", "created_at", "updated_at"
        )

    def get_participant_name(self, obj):
        return obj.user.get_full_name() or obj.user.email

    def validate(self, attrs):
        hackathon = self.context.get("hackathon") or getattr(self.instance, "hackathon", None)
        problem = attrs.get("selected_problem")
        if problem and hackathon and problem.hackathon_id != hackathon.id:
            raise serializers.ValidationError({
                "selected_problem": "This problem statement belongs to another hackathon."
            })
        if problem and not problem.is_published:
            raise serializers.ValidationError({
                "selected_problem": "This problem statement is not open for participants."
            })
        if self.instance is None and not attrs.get("agreed_to_rules"):
            raise serializers.ValidationError({
                "agreed_to_rules": "You must accept the event rules and code of conduct."
            })
        return attrs


class HackathonRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HackathonRegistration
        fields = "__all__"
        read_only_fields = ("registered_at",)
