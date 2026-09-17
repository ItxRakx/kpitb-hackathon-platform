from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    TeamViewSet,
    TeamInviteViewSet,
    JoinByCodeView,
    LeaveTeamView,
    RemoveMemberView,
    TransferLeadershipView,
    LockRosterView,
    UnlockRosterView,
    AcceptTeamInviteView,
    DeclineTeamInviteView,
    HealthCheckView,
)

app_name = "teams"

router = DefaultRouter()
router.register(r"invites", TeamInviteViewSet, basename="team-invites")
router.register(r"", TeamViewSet, basename="team")

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("join-by-code/", JoinByCodeView.as_view(), name="join-by-code"),
    path("<int:team_id>/leave/", LeaveTeamView.as_view(), name="leave-team"),
    path(
        "<int:team_id>/members/<int:user_id>/remove/",
        RemoveMemberView.as_view(),
        name="remove-member",
    ),
    path(
        "<int:team_id>/transfer-leadership/",
        TransferLeadershipView.as_view(),
        name="transfer-leadership",
    ),
    path("<int:team_id>/lock-roster/", LockRosterView.as_view(), name="lock-roster"),
    path(
        "<int:team_id>/unlock-roster/",
        UnlockRosterView.as_view(),
        name="unlock-roster",
    ),
    path(
        "invites/<int:invite_id>/accept/",
        AcceptTeamInviteView.as_view(),
        name="accept-invite",
    ),
    path(
        "invites/<int:invite_id>/decline/",
        DeclineTeamInviteView.as_view(),
        name="decline-invite",
    ),
    path("", include(router.urls)),
]
