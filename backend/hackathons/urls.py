from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    HackathonViewSet,
    JudgingCriterionViewSet,
    RegisterTeamForHackathonView,
    MyRegistrationForHackathonView,
    HealthCheckView,
    ProblemStatementViewSet,
    ParticipantEnrollmentView,
    ParticipantEnrollmentAdminViewSet,
    MyParticipantEnrollmentsView,
)

app_name = "hackathons"

router = DefaultRouter()
router.register(r"enrollments", ParticipantEnrollmentAdminViewSet, basename="participant-enrollment")
router.register(r"problems", ProblemStatementViewSet, basename="problem-statement")
router.register(r"criteria", JudgingCriterionViewSet, basename="criteria")
router.register(r"", HackathonViewSet, basename="hackathon")

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path(
        "enrollments/me/",
        MyParticipantEnrollmentsView.as_view(),
        name="my-participant-enrollments",
    ),
    path(
        "<slug:hackathon_slug>/enrollment/",
        ParticipantEnrollmentView.as_view(),
        name="participant-enrollment",
    ),
    path(
        "<slug:hackathon_slug>/registrations/me/",
        MyRegistrationForHackathonView.as_view(),
        name="my-registration",
    ),
    path(
        "<slug:hackathon_slug>/my-registration/",
        MyRegistrationForHackathonView.as_view(),
        name="my-registration-legacy",
    ),
    path(
        "<slug:hackathon_slug>/registrations/",
        RegisterTeamForHackathonView.as_view(),
        name="register-team",
    ),
    path(
        "<slug:hackathon_slug>/register-team/",
        RegisterTeamForHackathonView.as_view(),
        name="register-team-legacy",
    ),
    path("", include(router.urls)),
]
