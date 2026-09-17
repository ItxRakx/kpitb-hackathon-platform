from django.contrib import admin

from .models import Team, TeamMembership, TeamInvite


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "hackathon",
        "problem_statement",
        "invite_code",
        "member_count",
        "is_roster_locked",
        "created_at",
    )
    list_filter = ("is_roster_locked", "hackathon", "problem_statement", "created_at")
    search_fields = ("name", "tagline", "invite_code", "hackathon__title", "track")
    readonly_fields = ("invite_code", "created_at", "updated_at")
    list_select_related = ("hackathon", "problem_statement")
    date_hierarchy = "created_at"

    def member_count(self, obj):
        return obj.member_count


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "team", "hackathon", "is_leader", "role", "joined_at")
    list_filter = ("is_leader", "role", "joined_at")
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "team__name",
        "team__hackathon__title",
    )
    list_select_related = ("user", "team", "team__hackathon")
    date_hierarchy = "joined_at"
    readonly_fields = ("joined_at",)

    def hackathon(self, obj):
        return obj.team.hackathon.title


@admin.register(TeamInvite)
class TeamInviteAdmin(admin.ModelAdmin):
    list_display = ("email", "team", "status", "invited_by", "expires_at", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("email", "team__name", "invited_by__email", "code")
    list_select_related = ("team", "invited_by")
    date_hierarchy = "created_at"
    readonly_fields = ("code", "created_at")
