from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "category", "is_read", "created_at")
    list_filter = ("category", "created_at", "read_at")
    search_fields = ("user__email", "title", "body")
    list_select_related = ("user",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"

    def is_read(self, obj):
        return obj.is_read

    is_read.boolean = True
