from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .models import (
    Hackathon, ProblemStatement, ParticipantEnrollment,
    JudgingCriterion, HackathonRegistration,
)
from teams.models import Team, TeamMembership
from .serializers import (
    HackathonSerializer,
    HackathonListSerializer,
    JudgingCriterionSerializer,
    HackathonRegistrationSerializer,
    ProblemStatementSerializer,
    ParticipantEnrollmentSerializer,
)


class HackathonViewSet(viewsets.ModelViewSet):
    lookup_field = "slug"
    queryset = Hackathon.objects.all()
    filterset_fields = ["is_active", "starts_at", "ends_at"]
    search_fields = ["title", "tagline"]
    ordering_fields = ["starts_at", "ends_at", "registration_closes_at"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset().annotate(
            judging_criteria_count=Count("judging_criteria", distinct=True),
            problem_count=Count(
                "problem_statements",
                filter=Q(problem_statements__is_published=True),
                distinct=True,
            ),
            participant_count=Count(
                "participant_enrollments",
                filter=Q(participant_enrollments__status__in=("registered", "approved")),
                distinct=True,
            ),
            team_count=Count("teams", distinct=True),
        )
        user = self.request.user
        scope = self.request.query_params.get("scope")
        now = timezone.now()
        if scope == "upcoming":
            qs = qs.filter(starts_at__gt=now)
        elif scope == "past":
            qs = qs.filter(ends_at__lt=now)
        elif scope == "current":
            qs = qs.filter(starts_at__lte=now, ends_at__gte=now)
        if self.action in ("list",) and not (user.is_authenticated and user.is_staff):
            qs = qs.filter(is_active=True)
        return qs.select_related().order_by("-starts_at")

    def get_serializer_class(self):
        if self.action == "list":
            return HackathonListSerializer
        return HackathonSerializer


class ProblemStatementViewSet(viewsets.ModelViewSet):
    serializer_class = ProblemStatementSerializer
    queryset = ProblemStatement.objects.select_related("hackathon").all()
    search_fields = ["title", "category", "summary", "description"]
    ordering_fields = ["category", "title", "created_at"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        hackathon = self.request.query_params.get("hackathon")
        if hackathon:
            if str(hackathon).isdigit():
                qs = qs.filter(hackathon_id=hackathon)
            else:
                qs = qs.filter(hackathon__slug=hackathon)
        if not (user.is_authenticated and user.is_staff):
            qs = qs.filter(is_published=True, hackathon__is_active=True)
        return qs


class ParticipantEnrollmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get_hackathon(self, hackathon_slug):
        try:
            return Hackathon.objects.get(slug=hackathon_slug)
        except Hackathon.DoesNotExist:
            raise NotFound("Hackathon not found.")

    def get(self, request, hackathon_slug=None):
        hackathon = self.get_hackathon(hackathon_slug)
        try:
            enrollment = ParticipantEnrollment.objects.select_related(
                "hackathon", "user", "selected_problem"
            ).get(hackathon=hackathon, user=request.user)
        except ParticipantEnrollment.DoesNotExist:
            raise NotFound("You have not registered for this hackathon yet.")
        return Response(ParticipantEnrollmentSerializer(enrollment).data)

    def post(self, request, hackathon_slug=None):
        hackathon = self.get_hackathon(hackathon_slug)
        if not hackathon.is_registration_open:
            raise ValidationError({
                "detail": "Hackathon registration is not open.",
                "code": "REGISTRATION_CLOSED",
            })
        if ParticipantEnrollment.objects.filter(hackathon=hackathon, user=request.user).exists():
            return Response(
                {"detail": "You are already registered for this hackathon.", "code": "ALREADY_ENROLLED"},
                status=status.HTTP_409_CONFLICT,
            )
        profile = request.user.profile
        if not profile.is_complete:
            raise ValidationError({
                "detail": "Complete your participant profile before registering.",
                "code": "PROFILE_INCOMPLETE",
            })
        serializer = ParticipantEnrollmentSerializer(
            data=request.data, context={"request": request, "hackathon": hackathon}
        )
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save(hackathon=hackathon, user=request.user)
        return Response(
            ParticipantEnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED,
        )

    def patch(self, request, hackathon_slug=None):
        hackathon = self.get_hackathon(hackathon_slug)
        try:
            enrollment = ParticipantEnrollment.objects.get(
                hackathon=hackathon, user=request.user
            )
        except ParticipantEnrollment.DoesNotExist:
            raise NotFound("You have not registered for this hackathon yet.")
        serializer = ParticipantEnrollmentSerializer(
            enrollment,
            data=request.data,
            partial=True,
            context={"request": request, "hackathon": hackathon},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ParticipantEnrollmentAdminViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ParticipantEnrollmentSerializer
    permission_classes = [IsAdminUser]
    queryset = ParticipantEnrollment.objects.select_related(
        "hackathon", "user", "selected_problem"
    ).all()

    def get_queryset(self):
        qs = super().get_queryset()
        hackathon = self.request.query_params.get("hackathon")
        if hackathon:
            qs = qs.filter(hackathon__slug=hackathon)
        status_value = self.request.query_params.get("status")
        if status_value:
            qs = qs.filter(status=status_value)
        return qs


class MyParticipantEnrollmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = ParticipantEnrollment.objects.select_related(
            "hackathon", "user", "selected_problem"
        ).filter(user=request.user)
        return Response(ParticipantEnrollmentSerializer(enrollments, many=True).data)


class JudgingCriterionViewSet(viewsets.ModelViewSet):
    serializer_class = JudgingCriterionSerializer
    queryset = JudgingCriterion.objects.select_related("hackathon").all()

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        hackathon_slug = self.request.query_params.get("hackathon")
        if hackathon_slug:
            qs = qs.filter(hackathon__slug=hackathon_slug)
        return qs

    def perform_create(self, serializer):
        hackathon_id = self.request.data.get("hackathon")
        if hackathon_id:
            serializer.save(hackathon_id=hackathon_id)
        else:
            raise ValidationError({"hackathon": "hackathon is required."})


class RegisterTeamForHackathonView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, hackathon_slug=None):
        try:
            hackathon = Hackathon.objects.get(slug=hackathon_slug)
        except Hackathon.DoesNotExist:
            raise NotFound("Hackathon not found.")

        if not hackathon.is_registration_open:
            raise ValidationError(
                {
                    "detail": "Hackathon registration is not open.",
                    "code": "REGISTRATION_CLOSED",
                }
            )

        team_id = request.data.get("team_id")
        if not team_id:
            raise ValidationError({"team_id": "team_id is required."})

        try:
            team = Team.objects.select_related("hackathon").get(id=team_id)
        except Team.DoesNotExist:
            raise NotFound("Team not found.")

        if team.hackathon_id != hackathon.id:
            raise ValidationError(
                {
                    "detail": "Team does not belong to this hackathon.",
                    "code": "TEAM_WRONG_HACKATHON",
                }
            )

        if not team.memberships.filter(user=request.user, is_leader=True).exists():
            if not request.user.is_staff:
                raise PermissionDenied("Only the team leader can register the team.")

        if hackathon.require_roster_lock_to_register and not team.is_roster_locked:
            raise ValidationError(
                {
                    "detail": "Team roster must be locked before registration.",
                    "code": "ROSTER_NOT_LOCKED",
                }
            )

        if hackathon.problem_statements.filter(is_published=True).exists() and not team.problem_statement_id:
            raise ValidationError(
                {
                    "detail": "Choose a published problem statement before registering the team.",
                    "code": "PROBLEM_STATEMENT_REQUIRED",
                }
            )

        if hackathon.require_participant_enrollment:
            member_ids = list(team.memberships.values_list("user_id", flat=True))
            enrolled_ids = set(
                ParticipantEnrollment.objects.filter(
                    hackathon=hackathon,
                    user_id__in=member_ids,
                    status__in=("registered", "approved"),
                ).values_list("user_id", flat=True)
            )
            missing_members = team.memberships.exclude(user_id__in=enrolled_ids).select_related("user")
            if missing_members.exists():
                missing_names = [
                    membership.user.get_full_name() or membership.user.email
                    for membership in missing_members
                ]
                raise ValidationError({
                    "detail": "Every team member must register individually first: " + ", ".join(missing_names),
                    "code": "MEMBERS_NOT_ENROLLED",
                })

        roster_size = team.memberships.count()
        if roster_size < hackathon.team_min_size:
            raise ValidationError(
                {
                    "detail": f"Team size {roster_size} is below minimum of {hackathon.team_min_size}.",
                    "code": "ROSTER_TOO_SMALL",
                }
            )
        if roster_size > hackathon.team_max_size:
            raise ValidationError(
                {
                    "detail": f"Team size {roster_size} exceeds maximum of {hackathon.team_max_size}.",
                    "code": "ROSTER_TOO_LARGE",
                }
            )

        if HackathonRegistration.objects.filter(team=team, hackathon=hackathon).exists():
            return Response(
                {
                    "detail": "Team already registered for this hackathon.",
                    "code": "ALREADY_REGISTERED",
                },
                status=status.HTTP_409_CONFLICT,
            )

        registration = HackathonRegistration.objects.create(
            hackathon=hackathon,
            team=team,
            registered_by=request.user,
            status="confirmed",
        )
        return Response(
            HackathonRegistrationSerializer(registration).data,
            status=status.HTTP_201_CREATED,
        )


class MyRegistrationForHackathonView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, hackathon_slug=None):
        try:
            hackathon = Hackathon.objects.get(slug=hackathon_slug)
        except Hackathon.DoesNotExist:
            raise NotFound("Hackathon not found.")

        team_ids = TeamMembership.objects.filter(user=request.user).values_list("team_id", flat=True)
        registration = (
            HackathonRegistration.objects.filter(
                hackathon=hackathon, team_id__in=team_ids
            )
            .select_related("team", "hackathon", "registered_by")
            .first()
        )
        if not registration:
            raise NotFound("You have no registration for this hackathon.")
        return Response(HackathonRegistrationSerializer(registration).data)


class HealthCheckView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        return Response({"status": "ok", "app": "hackathons"}, status=status.HTTP_200_OK)
