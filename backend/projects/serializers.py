from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Project, ProjectAttachment, ProjectInquiry

User = get_user_model()


class ProjectAttachmentSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(required=False, allow_blank=True)
    attachment_type = serializers.CharField(required=False, default="other")
    file_url = serializers.CharField(read_only=True)
    file_size = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProjectAttachment
        fields = (
            "id",
            "display_name",
            "attachment_type",
            "file",
            "file_url",
            "file_size",
            "uploaded_by",
            "created_at",
        )
        read_only_fields = (
            "id",
            "file_url",
            "file_size",
            "uploaded_by",
            "created_at",
        )

    def validate(self, attrs):
        if not attrs.get("display_name") and attrs.get("file"):
            attrs["display_name"] = attrs["file"].name
        if attrs.get("attachment_type") == "documentation":
            attrs["attachment_type"] = "report"
        return attrs

    def validate_file(self, value):
        if value.size > 100 * 1024 * 1024:
            raise serializers.ValidationError("Each attachment must be 100 MB or smaller.")
        return value


class ProjectListSerializer(serializers.ModelSerializer):
    hackathon_title = serializers.CharField(source="hackathon.title", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    problem_statement_title = serializers.CharField(source="problem_statement.title", read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "title",
            "slug",
            "tagline",
            "short_description",
            "track",
            "build_mode",
            "technologies",
            "status",
            "is_public",
            "hackathon",
            "hackathon_title",
            "team",
            "team_name",
            "problem_statement",
            "problem_statement_title",
            "repo_url",
            "demo_url",
            "demo_video_url",
            "submitted_at",
            "created_at",
        )


class ProjectDetailSerializer(serializers.ModelSerializer):
    attachments = ProjectAttachmentSerializer(many=True, read_only=True)
    is_leader = serializers.SerializerMethodField()
    hackathon_title = serializers.CharField(source="hackathon.title", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    problem_statement_title = serializers.CharField(source="problem_statement.title", read_only=True)

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = (
            "slug",
            "team",
            "hackathon",
            "submitted_at",
            "created_at",
            "updated_at",
        )

    def get_is_leader(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.team.memberships.filter(user=request.user, is_leader=True).exists()


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "id",
            "slug",
            "title",
            "tagline",
            "short_description",
            "description",
            "track",
            "build_mode",
            "technologies",
            "repo_url",
            "demo_url",
            "demo_video_url",
            "status",
            "is_public",
        )
        read_only_fields = ("id", "slug")


class ProjectInquirySerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    project_title = serializers.CharField(source="project.title", read_only=True)
    hackathon_title = serializers.CharField(source="hackathon.title", read_only=True)

    class Meta:
        model = ProjectInquiry
        fields = (
            "id", "created_by", "created_by_name", "created_by_email", "hackathon",
            "hackathon_title", "project", "project_title", "subject", "message", "status",
            "admin_response", "responded_by", "responded_at", "created_at", "updated_at"
        )
        read_only_fields = (
            "created_by", "status", "admin_response", "responded_by", "responded_at",
            "created_at", "updated_at"
        )

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() or obj.created_by.email
