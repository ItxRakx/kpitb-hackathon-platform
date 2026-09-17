from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

from .models import ParticipantProfile

User = get_user_model()


class ParticipantProfileInline(admin.StackedInline):
    model = ParticipantProfile
    can_delete = False
    raw_id_fields = ("user",)
    fieldsets = (
        (None, {"fields": (
            "phone", "institution", "district", "education_level", "skills", "bio",
            "portfolio_url", "github_url", "is_judge", "is_verified"
        )}),
    )


@admin.register(ParticipantProfile)
class ParticipantProfileAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user_email", "district", "institution", "is_judge", "is_verified", "created_at")
    list_filter = ("district", "education_level", "is_judge", "is_verified", "created_at")
    search_fields = ("user__email", "user__first_name", "user__last_name", "institution", "district", "skills")
    raw_id_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("user",)

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "Email"


if User in admin.site._registry:
    admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (ParticipantProfileInline,)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")
    search_fields = ("email", "first_name", "last_name", "username")
    ordering = ("-date_joined",)
    readonly_fields = ("last_login", "date_joined")
