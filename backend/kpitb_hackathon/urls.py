from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/accounts/", include("accounts.urls", namespace="accounts")),
    path("api/v1/hackathons/", include("hackathons.urls", namespace="hackathons")),
    path("api/v1/teams/", include("teams.urls", namespace="teams")),
    path("api/v1/projects/", include("projects.urls", namespace="projects")),
    path("api/v1/judging/", include("judging.urls", namespace="judging")),
    path("api/v1/notifications/", include("notifications.urls", namespace="notifications")),
]
