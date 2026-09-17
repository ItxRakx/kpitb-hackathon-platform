from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ProjectViewSet,
    ProjectAttachmentViewSet,
    HealthCheckView,
    ProjectInquiryViewSet,
)

app_name = "projects"

router = DefaultRouter()
router.register(r"inquiries", ProjectInquiryViewSet, basename="project-inquiries")
router.register(
    r"(?P<project_pk>[^/.]+)/attachments",
    ProjectAttachmentViewSet,
    basename="project-attachments",
)
router.register(r"attachments", ProjectAttachmentViewSet, basename="attachments")
router.register(r"", ProjectViewSet, basename="project")

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("", include(router.urls)),
]
