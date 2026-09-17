from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status, parsers
from rest_framework.decorators import action
from rest_framework.exceptions import (
    APIException,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hackathons.models import HackathonRegistration
from notifications.models import notify
from teams.models import Team, TeamMembership
from .models import Project, ProjectAttachment, ProjectInquiry
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateUpdateSerializer,
    ProjectAttachmentSerializer,
    ProjectInquirySerializer,
)


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflict."
    default_code = "conflict"


class ProjectViewSet(viewsets.ModelViewSet):
    lookup_field = "slug"
    queryset = Project.objects.select_related(
        "team", "hackathon", "problem_statement"
    ).prefetch_related("attachments").all()
    filterset_fields = ["hackathon", "status", "build_mode", "track", "is_public"]
    search_fields = ["title", "slug", "tagline", "short_description", "description"]
    ordering_fields = ["submitted_at", "created_at"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        hackathon_slug = self.request.query_params.get("hackathon")
        if hackathon_slug:
            qs = qs.filter(hackathon__slug=hackathon_slug)
        # Default to public-only for non-staff list queries. Allow ?is_public=false for staff/leaders
        is_public_param = self.request.query_params.get("is_public")
        if is_public_param is None:
            if self.action == "list" and not (user.is_authenticated and user.is_staff):
                qs = qs.filter(is_public=True)
            elif self.action != "list" and not (user.is_authenticated and user.is_staff):
                if user.is_authenticated:
                    my_teams = TeamMembership.objects.filter(
                        user=user
                    ).values_list("team_id", flat=True)
                    qs = qs.filter(Q(is_public=True) | Q(team_id__in=list(my_teams)))
                else:
                    qs = qs.filter(is_public=True)
        elif is_public_param.lower() in ("false", "0"):
            if not (user.is_authenticated and user.is_staff):
                if user.is_authenticated:
                    # Only show own team's private projects
                    my_teams = TeamMembership.objects.filter(
                        user=user
                    ).values_list("team_id", flat=True)
                    qs = qs.filter(
                        Q(is_public=True) | Q(team_id__in=list(my_teams))
                    )
                else:
                    qs = qs.filter(is_public=True)
        elif is_public_param.lower() in ("true", "1"):
            qs = qs.filter(is_public=True)
        # If results are published for the hackathon, sort by aggregate score
        return qs.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        if self.action in ("create", "update", "partial_update"):
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer

    def perform_create(self, serializer):
        team_id = self.request.data.get("team_id") or self.request.data.get("team")
        hackathon_id = self.request.data.get("hackathon_id")
        if not team_id:
            raise ValidationError({"team_id": "team_id is required."})
        try:
            team = Team.objects.select_related("hackathon").get(id=team_id)
        except Team.DoesNotExist:
            raise NotFound("Team not found.")
        hackathon = team.hackathon
        if not team.memberships.filter(user=self.request.user, is_leader=True).exists():
            if not self.request.user.is_staff:
                raise PermissionDenied("Only the team leader can create the project.")
        if not HackathonRegistration.objects.filter(
            team=team, hackathon=hackathon, status="confirmed"
        ).exists():
            raise ConflictError(
                {"detail": "Team must be registered for the hackathon first.",
                "code": "TEAM_NOT_REGISTERED"}
            )
        if Project.objects.filter(team=team).exists():
            raise ValidationError(
                {"detail": "Project already exists for this team.",
                "code": "PROJECT_ALREADY_EXISTS"}
            )
        project = serializer.save(
            team=team,
            hackathon=hackathon,
            problem_statement=team.problem_statement,
        )
        return project

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        if project.status in ("submitted", "under_review", "shortlisted", "winner", "rejected"):
            if not request.user.is_staff:
                raise PermissionDenied("Project is locked and cannot be edited.")
        if not project.team.memberships.filter(user=request.user, is_leader=True).exists():
            if not request.user.is_staff:
                raise PermissionDenied("Only the team leader can edit the project.")
        result = super().update(request, *args, **kwargs)
        return result

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="submit", permission_classes=[IsAuthenticated])
    def submit(self, request, slug=None):
        project = self.get_object()
        if not project.team.memberships.filter(user=request.user, is_leader=True).exists():
            if not request.user.is_staff:
                raise PermissionDenied("Only the team leader can submit the project.")
        if project.status == "submitted":
            raise ValidationError(
                {"detail": "Project is already submitted.", "code": "ALREADY_SUBMITTED"}
            )
        project.status = "submitted"
        project.submitted_at = timezone.now()
        # Make public on submission if hackathon has ended
        if project.hackathon.is_completed or request.data.get("make_public"):
            project.is_public = True
        project.save(update_fields=["status", "submitted_at", "is_public", "updated_at"])
        return Response(ProjectDetailSerializer(project, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="unlock", permission_classes=[IsAuthenticated])
    def unlock(self, request, slug=None):
        if not request.user.is_staff:
            raise PermissionDenied("Only staff can unlock submissions.")
        project = self.get_object()
        if project.status == "submitted":
            project.status = "draft"
            project.submitted_at = None
            project.save(update_fields=["status", "submitted_at", "updated_at"])
        return Response(ProjectDetailSerializer(project, context={"request": request}).data)


class ProjectAttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectAttachmentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    queryset = ProjectAttachment.objects.select_related(
        "project", "uploaded_by"
    ).all()

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project") or self.kwargs.get("project_pk")
        if project_id:
            qs = qs.filter(project_id=project_id)
        elif self.action in ("list", "retrieve"):
            # Public users only see attachments of public projects
            if not (self.request.user.is_authenticated and self.request.user.is_staff):
                qs = qs.filter(project__is_public=True)
        return qs

    def perform_create(self, serializer):
        project_id = self.request.data.get("project") or self.request.data.get("project_id")
        if not project_id:
            raise ValidationError({"project": "project is required."})
        try:
            project = Project.objects.select_related("team").get(id=project_id)
        except Project.DoesNotExist:
            raise NotFound("Project not found.")
        if not project.team.memberships.filter(user=self.request.user, is_leader=True).exists():
            if not self.request.user.is_staff:
                raise PermissionDenied("Only the team leader can upload attachments.")
        if project.status in ("submitted", "under_review", "shortlisted", "winner", "rejected"):
            if not self.request.user.is_staff:
                raise PermissionDenied("Project is locked.")
        serializer.save(project=project, uploaded_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        attachment = self.get_object()
        project = attachment.project
        if not project.team.memberships.filter(user=request.user, is_leader=True).exists():
            if not request.user.is_staff:
                raise PermissionDenied("Only the team leader can delete attachments.")
        return super().destroy(request, *args, **kwargs)


class ProjectInquiryViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectInquirySerializer
    permission_classes = [IsAuthenticated]
    queryset = ProjectInquiry.objects.select_related(
        "created_by", "hackathon", "project", "responded_by"
    ).all()
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(created_by=self.request.user)
        status_value = self.request.query_params.get("status")
        if status_value:
            qs = qs.filter(status=status_value)
        return qs

    def perform_create(self, serializer):
        project = serializer.validated_data.get("project")
        hackathon = serializer.validated_data.get("hackathon")
        if project:
            if not self.request.user.is_staff and not project.team.memberships.filter(
                user=self.request.user
            ).exists():
                raise PermissionDenied("You can only contact organizers about your own project.")
            hackathon = project.hackathon
        serializer.save(created_by=self.request.user, hackathon=hackathon)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Only organizers can answer or close inquiries.")
        inquiry = self.get_object()
        allowed = {key: request.data.get(key) for key in ("status", "admin_response") if key in request.data}
        serializer = self.get_serializer(inquiry, data=allowed, partial=True)
        serializer.fields["status"].read_only = False
        serializer.fields["admin_response"].read_only = False
        serializer.is_valid(raise_exception=True)
        response_text = serializer.validated_data.get("admin_response", inquiry.admin_response)
        status_value = serializer.validated_data.get("status", inquiry.status)
        if response_text and status_value == "open":
            status_value = "answered"
        serializer.save(
            status=status_value,
            responded_by=request.user,
            responded_at=timezone.now() if response_text else inquiry.responded_at,
        )
        if response_text:
            notify(
                inquiry.created_by,
                "Organizer replied to your question",
                f"Your question '{inquiry.subject}' has a new response.",
                "system",
            )
        return Response(serializer.data)


class HealthCheckView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        return Response({"status": "ok", "app": "projects"}, status=status.HTTP_200_OK)
