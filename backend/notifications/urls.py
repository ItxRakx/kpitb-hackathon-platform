from django.urls import path

from .views import (
    NotificationListView,
    MarkReadView,
    MarkAllReadView,
    HealthCheckView,
)

app_name = "notifications"

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("", NotificationListView.as_view(), name="notification-list"),
    path("<int:pk>/read/", MarkReadView.as_view(), name="mark-read"),
    path("<int:pk>/mark-read/", MarkReadView.as_view(), name="mark-read-alias"),
    path("mark-all-read/", MarkAllReadView.as_view(), name="mark-all-read"),
]
