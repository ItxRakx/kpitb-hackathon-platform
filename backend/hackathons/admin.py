from django.contrib import admin

from .models import (
    Hackathon, ProblemStatement, ParticipantEnrollment,
    JudgingCriterion, HackathonRegistration,
)


@admin.register(Hackathon)
class HackathonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "is_active",
        "is_registration_open",
        "team_min_size",
        "team_max_size",
        "starts_at",
        "ends_at",
    )
    list_filter = (
        "is_active",
        "results_published",
        "require_roster_lock_to_register",
        "require_participant_enrollment",
        "starts_at",
        "ends_at",
    )
    search_fields = ("title", "slug", "tagline", "description")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "starts_at"

    def is_registration_open(self, obj):
        return obj.is_registration_open

    is_registration_open.boolean = True


@admin.register(ProblemStatement)
class ProblemStatementAdmin(admin.ModelAdmin):
    list_display = ("title", "hackathon", "category", "difficulty", "is_published", "updated_at")
    list_filter = ("is_published", "difficulty", "category", "hackathon")
    search_fields = ("title", "summary", "description", "deliverables")
    list_select_related = ("hackathon",)
    readonly_fields = ("slug", "created_at", "updated_at")


@admin.register(ParticipantEnrollment)
class ParticipantEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "user", "hackathon", "primary_role", "participation_preference",
        "attendance_mode", "status", "created_at"
    )
    list_filter = (
        "status", "participation_preference", "primary_role", "experience_level",
        "attendance_mode", "hackathon"
    )
    search_fields = (
        "user__email", "user__first_name", "user__last_name", "motivation",
        "selected_problem__title"
    )
    list_select_related = ("user", "hackathon", "selected_problem")
    readonly_fields = ("created_at", "updated_at")


@admin.register(JudgingCriterion)
class JudgingCriterionAdmin(admin.ModelAdmin):
    list_display = ("hackathon", "name", "weight", "max_score", "order")
    list_filter = ("hackathon",)
    search_fields = ("name", "description", "hackathon__title")
    list_select_related = ("hackathon",)
    ordering = ("hackathon", "order")


@admin.register(HackathonRegistration)
class HackathonRegistrationAdmin(admin.ModelAdmin):
    list_display = ("team", "hackathon", "registered_by", "status", "registered_at")
    list_filter = ("status", "registered_at", "hackathon")
    search_fields = ("team__name", "hackathon__title", "registered_by__email")
    list_select_related = ("team", "hackathon", "registered_by")
    date_hierarchy = "registered_at"
    readonly_fields = ("registered_at",)
