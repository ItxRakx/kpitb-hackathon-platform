from django.contrib import admin

from .models import JudgeAssignment, ProjectJudgeAssignment, Score


@admin.register(JudgeAssignment)
class JudgeAssignmentAdmin(admin.ModelAdmin):
    list_display = ("judge", "hackathon", "assigned_at")
    list_filter = ("assigned_at", "hackathon")
    search_fields = ("judge__email", "hackathon__title")
    list_select_related = ("judge", "hackathon")
    readonly_fields = ("assigned_at",)


@admin.register(ProjectJudgeAssignment)
class ProjectJudgeAssignmentAdmin(admin.ModelAdmin):
    list_display = ("judge", "project", "assigned_at")
    list_filter = ("assigned_at",)
    search_fields = ("judge__email", "project__title")
    list_select_related = ("judge", "project")
    readonly_fields = ("assigned_at",)


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = (
        "judge",
        "project",
        "criterion",
        "value",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "judge__email",
        "project__title",
        "criterion__name",
        "comment",
    )
    list_select_related = ("judge", "project", "criterion")
    readonly_fields = ("created_at", "updated_at")
