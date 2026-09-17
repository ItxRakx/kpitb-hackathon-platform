from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from hackathons.models import Hackathon, JudgingCriterion
from projects.models import Project
from projects.serializers import ProjectDetailSerializer
from teams.models import TeamMembership
from .models import JudgeAssignment, ProjectJudgeAssignment, Score
from .serializers import (
    JudgeAssignmentSerializer,
    ProjectJudgeAssignmentSerializer,
    ScoreSerializer,
    ScoreUpsertSerializer,
)


def _is_assigned_judge_for_hackathon(user, hackathon) -> bool:
    if user.is_staff:
        return True
    return JudgeAssignment.objects.filter(judge=user, hackathon=hackathon).exists()


def _is_assigned_judge_for_project(user, project) -> bool:
    if user.is_staff:
        return True
    if not JudgeAssignment.objects.filter(judge=user, hackathon=project.hackathon).exists():
        return False
    project_level = ProjectJudgeAssignment.objects.filter(project=project).exists()
    if project_level:
        return ProjectJudgeAssignment.objects.filter(judge=user, project=project).exists()
    return True


class JudgeAssignmentViewSet(viewsets.ModelViewSet):
    queryset = JudgeAssignment.objects.select_related("judge", "hackathon").all()
    serializer_class = JudgeAssignmentSerializer
    permission_classes = [IsAdminUser]


class ProjectJudgeAssignmentViewSet(viewsets.ModelViewSet):
    queryset = ProjectJudgeAssignment.objects.select_related("judge", "project").all()
    serializer_class = ProjectJudgeAssignmentSerializer
    permission_classes = [IsAdminUser]


class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.select_related("judge", "project", "criterion").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ScoreUpsertSerializer
        return ScoreSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff:
            return qs
        return qs.filter(judge=user)

    def perform_create(self, serializer):
        project_id = self.request.data.get("project")
        criterion_id = self.request.data.get("criterion")
        if not project_id or not criterion_id:
            raise ValidationError({"project": "project and criterion are required."})
        try:
            project = Project.objects.select_related(
                "team", "hackathon"
            ).prefetch_related("team__memberships").get(id=project_id)
        except Project.DoesNotExist:
            raise NotFound("Project not found.")
        try:
            criterion = JudgingCriterion.objects.get(id=criterion_id)
        except JudgingCriterion.DoesNotExist:
            raise NotFound("Criterion not found.")
        if criterion.hackathon_id != project.hackathon_id:
            raise ValidationError(
                {"detail": "Criterion must belong to the project's hackathon.",
                "code": "CRITERION_HACKATHON_MISMATCH"}
            )
        if not _is_assigned_judge_for_project(self.request.user, project):
            raise PermissionDenied("You are not assigned to judge this project.")
        # Conflict of interest guard
        user_ids = [u.user_id for u in project.team.memberships.all()]
        if self.request.user.id in user_ids:
            raise PermissionDenied(
                {"detail": "Conflict of interest: you cannot score your own team's project.",
                 "code": "CONFLICT_OF_INTEREST"}
            )
        value = serializer.validated_data.get("value", 0)
        if value < 0:
            value = 0
        if value > criterion.max_score:
            value = criterion.max_score
        comment = serializer.validated_data.get("comment", "")
        score, created = Score.objects.update_or_create(
            judge=self.request.user,
            project=project,
            criterion=criterion,
            defaults={"value": value, "comment": comment},
        )
        return score

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Find created/updated instance
        project_id = request.data.get("project")
        criterion_id = request.data.get("criterion")
        instance = Score.objects.filter(
            judge=request.user, project_id=project_id, criterion_id=criterion_id
        ).first()
        return Response(
            ScoreSerializer(instance).data,
            status=status.HTTP_200_OK if instance else status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_staff and instance.judge_id != request.user.id:
            raise PermissionDenied("Only the judge or staff can edit this score.")
        if instance.judge_id == request.user.id:
            # Re-check assignment/COI on edit
            project = instance.project
            if not _is_assigned_judge_for_project(request.user, project):
                raise PermissionDenied("You are not assigned to judge this project.")
            user_ids = [u.user_id for u in project.team.memberships.all()]
            if request.user.id in user_ids:
                return Response(
                    {"detail": "Conflict of interest: you cannot score your own team's project.",
                    "code": "CONFLICT_OF_INTEREST"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_staff and instance.judge_id != request.user.id:
            raise PermissionDenied("Only the judge or staff can delete this score.")
        return super().destroy(request, *args, **kwargs)


class JudgeHackathonProjectsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, hackathon_slug=None):
        try:
            hackathon = Hackathon.objects.get(slug=hackathon_slug)
        except Hackathon.DoesNotExist:
            raise NotFound("Hackathon not found.")
        if not _is_assigned_judge_for_hackathon(request.user, hackathon):
            raise PermissionDenied("You are not assigned to judge this hackathon.")
        projects = Project.objects.filter(
            hackathon=hackathon, status__in=["submitted", "under_review", "shortlisted", "winner"]
        ).select_related("team", "hackathon").prefetch_related("attachments")
        if ProjectJudgeAssignment.objects.filter(project__hackathon=hackathon).exists():
            projects = projects.filter(
                Q(judge_assignments__judge=request.user)
                | Q(team__memberships__user=request.user)  # shouldn't happen, but COI guard
            ).distinct()
        data = ProjectDetailSerializer(
            projects, many=True, context={"request": request}
        ).data
        # Add aggregate scores
        for item, project in zip(data, projects):
            item["aggregate_score"] = _compute_aggregate(project)
            item["my_scores"] = ScoreSerializer(
                Score.objects.filter(judge=request.user, project=project),
                many=True,
            ).data
        return Response(data)


def _compute_aggregate(project) -> dict:
    """Weighted sum of scores per judge, averaged across judges.
    Return dict with weighted_total and judge_count.
    Uses ORM Sum + division in Python for correctness.
    """
    scores = Score.objects.filter(project=project).select_related("criterion")
    if not scores.exists():
        return {"weighted_total": None, "judge_count": 0, "max_possible": None}
    per_judge = {}
    weight_sum_total = 0.0
    for s in scores:
        weight = s.criterion.weight if s.criterion else 1.0
        max_score = s.criterion.max_score if s.criterion else 100.0
        normalized = (s.value / max_score) * weight if max_score else 0.0
        per_judge.setdefault(s.judge_id, 0.0)
        per_judge[s.judge_id] += normalized
        weight_sum_total += weight
    if not per_judge:
        return {"weighted_total": None, "judge_count": 0, "max_possible": weight_sum_total or None}
    total = sum(per_judge.values()) / len(per_judge)
    return {
        "weighted_total": round(total, 3),
        "judge_count": len(per_judge),
        "max_possible": weight_sum_total or 1.0,
    }


class ProjectAggregateScoreView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, project_pk=None):
        try:
            project = Project.objects.get(id=project_pk)
        except Project.DoesNotExist:
            raise NotFound("Project not found.")
        if not project.hackathon.results_published and not (
            request.user.is_authenticated and (
                request.user.is_staff
                or project.team.memberships.filter(user=request.user).exists()
                or JudgeAssignment.objects.filter(judge=request.user, hackathon=project.hackathon).exists()
            )
        ):
            raise PermissionDenied("Results are not published yet.")
        return Response(_compute_aggregate(project))


class HealthCheckView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        return Response({"status": "ok", "app": "judging"}, status=status.HTTP_200_OK)
