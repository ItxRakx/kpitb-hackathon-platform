from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    JudgeAssignmentViewSet,
    ProjectJudgeAssignmentViewSet,
    ScoreViewSet,
    JudgeHackathonProjectsListView,
    ProjectAggregateScoreView,
    HealthCheckView,
)

app_name = "judging"

router = DefaultRouter()
router.register(r"assignments", JudgeAssignmentViewSet, basename="judge-assignments")
router.register(
    r"project-assignments", ProjectJudgeAssignmentViewSet,
    basename="project-judge-assignments",
)
router.register(r"scores", ScoreViewSet, basename="scores")

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path(
        "hackathons/<slug:hackathon_slug>/projects/",
        JudgeHackathonProjectsListView.as_view(),
        name="judge-hackathon-projects",
    ),
    path(
        "projects/<int:project_pk>/aggregate-score/",
        ProjectAggregateScoreView.as_view(),
        name="project-aggregate-score",
    ),
    path("", include(router.urls)),
]
