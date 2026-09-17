from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Team, TeamMembership, TeamInvite

User = get_user_model()


class TeamMemberUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name")


class TeamMembershipSerializer(serializers.ModelSerializer):
    user = TeamMemberUserSerializer(read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = TeamMembership
        fields = (
            "id",
            "user",
            "user_id",
            "is_leader",
            "role",
            "joined_at",
        )
        read_only_fields = ("id", "joined_at")


class TeamListSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)
    hackathon_title = serializers.CharField(source="hackathon.title", read_only=True)
    max_members = serializers.IntegerField(source="hackathon.team_max_size", read_only=True)
    problem_statement_title = serializers.CharField(source="problem_statement.title", read_only=True)
    is_leader = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()
    invite_code = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = (
            "id",
            "name",
            "tagline",
            "track",
            "problem_statement",
            "problem_statement_title",
            "hackathon",
            "hackathon_title",
            "invite_code",
            "is_roster_locked",
            "member_count",
            "max_members",
            "is_leader",
            "is_registered",
            "created_at",
        )

    def get_is_leader(self, obj):
        request = self.context.get("request")
        return bool(
            request and request.user.is_authenticated
            and obj.memberships.filter(user=request.user, is_leader=True).exists()
        )

    def get_is_registered(self, obj):
        return hasattr(obj, "hackathon_registration")

    def get_invite_code(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            if request.user.is_staff or obj.memberships.filter(user=request.user).exists():
                return obj.invite_code
        return ""


class TeamDetailSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)
    memberships = TeamMembershipSerializer(many=True, read_only=True)
    is_leader = serializers.SerializerMethodField()
    hackathon_title = serializers.CharField(source="hackathon.title", read_only=True)
    max_members = serializers.IntegerField(source="hackathon.team_max_size", read_only=True)
    problem_statement_title = serializers.CharField(source="problem_statement.title", read_only=True)
    is_registered = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = "__all__"
        read_only_fields = (
            "invite_code",
            "created_at",
            "updated_at",
            "is_roster_locked",
            "created_by",
        )

    def get_is_leader(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.memberships.filter(user=request.user, is_leader=True).exists()

    def get_is_registered(self, obj):
        return hasattr(obj, "hackathon_registration")


class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("id", "name", "tagline", "track", "hackathon", "problem_statement")
        read_only_fields = ("id",)

    def validate_name(self, value):
        hackathon = self.initial_data.get("hackathon")
        if hackathon and Team.objects.filter(hackathon_id=hackathon, name=value).exists():
            raise serializers.ValidationError(
                "A team with this name already exists in the hackathon.",
                code="DUPLICATE_TEAM_NAME",
            )
        return value

    def validate(self, attrs):
        problem = attrs.get("problem_statement")
        hackathon = attrs.get("hackathon")
        if problem and hackathon and problem.hackathon_id != hackathon.id:
            raise serializers.ValidationError({
                "problem_statement": "This problem statement belongs to another hackathon."
            })
        if problem and not problem.is_published:
            raise serializers.ValidationError({
                "problem_statement": "This problem statement is not open for teams."
            })
        return attrs


class JoinByCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=16)


class TransferLeadershipSerializer(serializers.Serializer):
    new_leader_id = serializers.IntegerField()


class TeamInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamInvite
        fields = "__all__"
        read_only_fields = ("code", "created_at", "status", "invited_by", "expires_at")
