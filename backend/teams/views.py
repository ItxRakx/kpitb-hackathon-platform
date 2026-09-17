from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as ModelValidationError
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hackathons.models import Hackathon, HackathonRegistration, ParticipantEnrollment
from notifications.models import notify
from .models import Team, TeamMembership, TeamInvite
from .serializers import (
    TeamListSerializer,
    TeamDetailSerializer,
    TeamCreateSerializer,
    TeamMembershipSerializer,
    TeamInviteSerializer,
    JoinByCodeSerializer,
    TransferLeadershipSerializer,
)

User = get_user_model()


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.select_related("hackathon", "problem_statement").prefetch_related(
        "memberships", "memberships__user"
    ).all()

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        hackathon = self.request.query_params.get("hackathon")
        if hackathon:
            try:
                qs = qs.filter(hackathon__slug=hackathon)
            except Exception:
                qs = qs.filter(hackathon_id=hackathon)
        mine = self.request.query_params.get("mine")
        if mine and self.request.user.is_authenticated:
            qs = qs.filter(memberships__user=self.request.user)
        return qs.distinct()

    def get_serializer_class(self):
        if self.action == "create":
            return TeamCreateSerializer
        if self.action == "list":
            return TeamListSerializer
        return TeamDetailSerializer

    def perform_create(self, serializer):
        hackathon_id = self.request.data.get("hackathon")
        if not hackathon_id:
            raise ValidationError({"hackathon": "hackathon is required."})
        try:
            hackathon = Hackathon.objects.get(id=hackathon_id)
        except Hackathon.DoesNotExist:
            try:
                hackathon = Hackathon.objects.get(slug=hackathon_id)
            except Hackathon.DoesNotExist:
                raise NotFound("Hackathon not found.")
        if TeamMembership.objects.filter(
            user=self.request.user, team__hackathon=hackathon
        ).exists():
            raise ValidationError(
                {
                    "detail": "You already belong to a team in this hackathon.",
                    "code": "DUPLICATE_HACKATHON_MEMBERSHIP",
                }
            )
        if hackathon.require_participant_enrollment and not ParticipantEnrollment.objects.filter(
            hackathon=hackathon,
            user=self.request.user,
            status__in=("registered", "approved"),
        ).exists():
            raise ValidationError({
                "detail": "Register yourself for this hackathon before creating a team.",
                "code": "PARTICIPANT_NOT_ENROLLED",
            })
        problem_statement = serializer.validated_data.get("problem_statement")
        if problem_statement and problem_statement.hackathon_id != hackathon.id:
            raise ValidationError({"problem_statement": "Problem statement does not belong to this hackathon."})
        team = serializer.save(hackathon=hackathon, created_by=self.request.user)
        TeamMembership.objects.create(
            team=team, user=self.request.user, is_leader=True, role="leader"
        )

    def update(self, request, *args, **kwargs):
        team = self.get_object()
        if not team.memberships.filter(user=request.user, is_leader=True).exists():
            if not request.user.is_staff:
                raise PermissionDenied("Only the team leader can edit this team.")
        return super().update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        team = self.get_object()
        if not request.user.is_staff and not team.memberships.filter(user=request.user).exists():
            raise PermissionDenied("Team roster is only visible to its members.")
        return Response(self.get_serializer(team).data)

    def destroy(self, request, *args, **kwargs):
        team = self.get_object()
        if not team.memberships.filter(user=request.user, is_leader=True).exists():
            if not request.user.is_staff:
                raise PermissionDenied("Only the team leader can delete this team.")
        if HackathonRegistration.objects.filter(team=team).exists():
            raise ValidationError(
                {
                    "detail": "Cannot delete a team that has registered for the hackathon.",
                    "code": "TEAM_ALREADY_REGISTERED",
                }
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="members", permission_classes=[IsAuthenticated])
    def members(self, request, pk=None):
        team = self.get_object()
        if not request.user.is_staff and not team.memberships.filter(user=request.user).exists():
            raise PermissionDenied("Team roster is only visible to its members.")
        memberships = team.memberships.select_related("user").all()
        return Response(TeamMembershipSerializer(memberships, many=True).data)


class JoinByCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = JoinByCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["invite_code"].strip().upper()
        try:
            team = Team.objects.select_related("hackathon").get(invite_code=code)
        except Team.DoesNotExist:
            raise NotFound("No team found with this invite code.")
        hackathon = team.hackathon
        if hackathon.require_participant_enrollment and not ParticipantEnrollment.objects.filter(
            hackathon=hackathon,
            user=request.user,
            status__in=("registered", "approved"),
        ).exists():
            raise ValidationError({
                "detail": "Register yourself for this hackathon before joining a team.",
                "code": "PARTICIPANT_NOT_ENROLLED",
            })
        if TeamMembership.objects.filter(user=request.user, team__hackathon=hackathon).exists():
            raise ValidationError(
                {
                    "detail": "You already belong to a team in this hackathon.",
                    "code": "DUPLICATE_HACKATHON_MEMBERSHIP",
                }
            )
        if team.is_roster_locked:
            raise PermissionDenied("Team roster is locked.")
        current_count = team.memberships.count()
        if current_count >= hackathon.team_max_size:
            return Response(
                {
                    "detail": f"Team is already full ({current_count}/{hackathon.team_max_size}).",
                    "code": "ROSTER_FULL",
                },
                status=status.HTTP_409_CONFLICT,
            )
        try:
            membership = TeamMembership.objects.create(
                team=team, user=request.user, is_leader=False, role="member"
            )
        except ModelValidationError as exc:
            raise ValidationError({"detail": str(exc)})
        return Response(
            TeamMembershipSerializer(membership).data, status=status.HTTP_201_CREATED
        )


class LeaveTeamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id=None):
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise NotFound("Team not found.")
        if team.is_roster_locked:
            raise PermissionDenied("Team roster is locked — cannot leave.")
        if HackathonRegistration.objects.filter(team=team).exists():
            raise ValidationError(
                {
                    "detail": "Cannot leave a team that has registered for the hackathon.",
                    "code": "TEAM_ALREADY_REGISTERED",
                }
            )
        membership = team.memberships.filter(user=request.user).first()
        if not membership:
            raise NotFound("You are not a member of this team.")
        if membership.is_leader:
            other_leaders = team.memberships.filter(is_leader=True).exclude(pk=membership.pk).exists()
            if not other_leaders:
                raise ValidationError(
                    {
                        "detail": "You are the only leader. Transfer leadership before leaving.",
                        "code": "LAST_LEADER",
                    }
                )
        membership.delete()
        return Response({"detail": "Left team successfully."})


class RemoveMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id=None, user_id=None):
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise NotFound("Team not found.")
        if not team.memberships.filter(user=request.user, is_leader=True).exists():
            if not request.user.is_staff:
                raise PermissionDenied("Only the team leader can remove members.")
        if team.is_roster_locked:
            raise PermissionDenied("Team roster is locked — cannot remove members.")
        membership = team.memberships.filter(user_id=user_id).first()
        if not membership:
            raise NotFound("Member not found in this team.")
        if membership.is_leader:
            raise ValidationError(
                {"detail": "Cannot remove a team leader.", "code": "CANNOT_REMOVE_LEADER"}
            )
        membership.delete()
        return Response({"detail": "Member removed."})


class TransferLeadershipView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id=None):
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise NotFound("Team not found.")
        if not team.memberships.filter(user=request.user, is_leader=True).exists():
            if not request.user.is_staff:
                raise PermissionDenied("Only the team leader can transfer leadership.")
        serializer = TransferLeadershipSerializer(data={
            "new_leader_id": request.data.get("new_leader_id")
            or request.data.get("new_leader_user_id")
        })
        serializer.is_valid(raise_exception=True)
        new_leader_id = serializer.validated_data["new_leader_id"]
        new_membership = team.memberships.filter(user_id=new_leader_id).first()
        if not new_membership:
            raise NotFound("Target user is not a member of this team.")
        current = team.memberships.filter(is_leader=True).all()
        for m in current:
            if m.user_id == request.user.id:
                m.is_leader = False
                m.role = "member"
                m.save(update_fields=["is_leader", "role"])
        new_membership.is_leader = True
        new_membership.role = "leader"
        new_membership.save(update_fields=["is_leader", "role"])
        return Response({"detail": "Leadership transferred."})


class LockRosterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id=None):
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise NotFound("Team not found.")
        if not team.memberships.filter(user=request.user, is_leader=True).exists():
            if not request.user.is_staff:
                raise PermissionDenied("Only the team leader can lock the roster.")
        roster_size = team.memberships.count()
        if roster_size < team.hackathon.team_min_size:
            raise ValidationError({
                "detail": f"Add at least {team.hackathon.team_min_size} members before locking the roster.",
                "code": "ROSTER_TOO_SMALL",
            })
        team.is_roster_locked = True
        team.save(update_fields=["is_roster_locked", "updated_at"])
        return Response({"detail": "Roster locked."})


class UnlockRosterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id=None):
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise NotFound("Team not found.")
        if not request.user.is_staff and not team.memberships.filter(user=request.user, is_leader=True).exists():
            raise PermissionDenied("Only staff or the team leader can unlock the roster.")
        team.is_roster_locked = False
        team.save(update_fields=["is_roster_locked", "updated_at"])
        return Response({"detail": "Roster unlocked."})


class TeamInviteViewSet(viewsets.ModelViewSet):
    queryset = TeamInvite.objects.select_related("team", "invited_by").all()
    serializer_class = TeamInviteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff:
            return qs
        # Show invites where user is invited or is team leader of the team
        return qs.filter(
            Q(email__iexact=user.email)
            | Q(team__memberships__user=user, team__memberships__is_leader=True)
        ).distinct()

    def perform_create(self, serializer):
        team_id = self.request.data.get("team") or self.request.data.get("team_id")
        if not team_id:
            raise ValidationError({"team": "team is required."})
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise NotFound("Team not found.")
        if not team.memberships.filter(user=self.request.user, is_leader=True).exists():
            if not self.request.user.is_staff:
                raise PermissionDenied("Only the team leader can send invites.")
        if team.is_roster_locked:
            raise PermissionDenied("Team roster is locked.")
        email = serializer.validated_data.get("email").lower().strip()
        if team.memberships.filter(user__email__iexact=email).exists():
            raise ValidationError({"email": "This participant is already on the team."})
        if TeamInvite.objects.filter(team=team, email__iexact=email, status="pending").exists():
            raise ValidationError({"email": "A pending invite already exists for this email."})
        reserved_places = team.memberships.count() + team.invites.filter(status="pending").count()
        if reserved_places >= team.hackathon.team_max_size:
            raise ValidationError({
                "detail": f"Team capacity is already reserved ({reserved_places}/{team.hackathon.team_max_size}).",
                "code": "ROSTER_FULL",
            })
        expires = timezone.now() + timedelta(days=7)
        try:
            invite = serializer.save(
                team=team, invited_by=self.request.user,
                status="pending", expires_at=expires
            )
            invited_user = User.objects.filter(email__iexact=email).first()
            if invited_user:
                notify(
                    invited_user,
                    f"Team invite from {team.name}",
                    f"Use invite code {team.invite_code} to join {team.name} for {team.hackathon.title}.",
                    "team",
                )
            return invite
        except Exception as exc:
            raise ValidationError({"detail": str(exc)})


class AcceptTeamInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invite_id=None):
        try:
            invite = TeamInvite.objects.select_related("team", "team__hackathon").get(id=invite_id)
        except TeamInvite.DoesNotExist:
            raise NotFound("Invite not found.")
        if invite.email.lower() != request.user.email.lower():
            raise PermissionDenied("This invite is not addressed to your email.")
        if invite.status != "pending":
            raise ValidationError(
                {"detail": f"Invite is already {invite.status}.", "code": "INVALID_INVITE_STATUS"}
            )
        if invite.is_expired:
            invite.status = "revoked"
            invite.save(update_fields=["status"])
            raise ValidationError({"detail": "Invite has expired.", "code": "EXPIRED"})
        team = invite.team
        hackathon = team.hackathon
        if hackathon.require_participant_enrollment and not ParticipantEnrollment.objects.filter(
            hackathon=hackathon,
            user=request.user,
            status__in=("registered", "approved"),
        ).exists():
            raise ValidationError({
                "detail": "Register yourself for this hackathon before accepting a team invite.",
                "code": "PARTICIPANT_NOT_ENROLLED",
            })
        if TeamMembership.objects.filter(user=request.user, team__hackathon=hackathon).exists():
            raise ValidationError(
                {"detail": "You already belong to a team in this hackathon.",
                "code": "DUPLICATE_HACKATHON_MEMBERSHIP"}
            )
        if team.is_roster_locked:
            raise PermissionDenied("Team roster is locked.")
        if team.memberships.count() >= hackathon.team_max_size:
            return Response(
                {"detail": "Team is full.", "code": "ROSTER_FULL"},
                status=status.HTTP_409_CONFLICT,
            )
        try:
            membership = TeamMembership.objects.create(
                team=team, user=request.user, is_leader=False, role="member"
            )
        except ModelValidationError as exc:
            raise ValidationError({"detail": str(exc)})
        invite.status = "accepted"
        invite.save(update_fields=["status"])
        return Response(
            TeamMembershipSerializer(membership).data, status=status.HTTP_201_CREATED
        )


class DeclineTeamInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invite_id=None):
        try:
            invite = TeamInvite.objects.get(id=invite_id)
        except TeamInvite.DoesNotExist:
            raise NotFound("Invite not found.")
        if invite.email.lower() != request.user.email.lower() and not request.user.is_staff:
            raise PermissionDenied("This invite is not addressed to your email.")
        invite.status = "revoked"
        invite.save(update_fields=["status"])
        return Response({"detail": "Invite declined."})


class HealthCheckView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        return Response({"status": "ok", "app": "teams"}, status=status.HTTP_200_OK)
