from django.contrib import admin

from .models import Project, ProjectAttachment, ProjectInquiry


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "hackathon",
        "team",
        "problem_statement",
        "status",
        "track",
        "build_mode",
        "is_public",
        "submitted_at",
    )
    list_filter = (
        "status",
        "build_mode",
        "is_public",
        "hackathon",
        "submitted_at",
    )
    search_fields = (
        "title",
        "slug",
        "tagline",
        "description",
        "team__name",
        "track",
    )
    list_select_related = ("team", "hackathon", "problem_statement")
    readonly_fields = ("slug", "created_at", "updated_at", "submitted_at")
    date_hierarchy = "submitted_at"


@admin.register(ProjectAttachment)
class ProjectAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "attachment_type",
        "project",
        "uploaded_by",
        "created_at",
    )
    list_filter = ("attachment_type", "created_at")
    search_fields = ("display_name", "project__title", "uploaded_by__email")
    list_select_related = ("project", "uploaded_by")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"


@admin.register(ProjectInquiry)
class ProjectInquiryAdmin(admin.ModelAdmin):
    list_display = ("subject", "created_by", "hackathon", "project", "status", "responded_by", "created_at")
    list_filter = ("status", "hackathon", "created_at")
    search_fields = ("subject", "message", "admin_response", "created_by__email", "project__title")
    list_select_related = ("created_by", "hackathon", "project", "responded_by")
    readonly_fields = ("created_at", "updated_at", "responded_at")
