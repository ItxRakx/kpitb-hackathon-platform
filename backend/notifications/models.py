from django.conf import settings
from django.db import models
from django.utils import timezone


NOTIFICATION_CATEGORIES = [
    ("info", "Info"),
    ("team", "Team"),
    ("judging", "Judging"),
    ("hackathon", "Hackathon"),
    ("alert", "Alert"),
]


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        db_index=True,
    )
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True, default="")
    category = models.CharField(
        max_length=30, choices=NOTIFICATION_CATEGORIES, default="info"
    )
    action_url = models.URLField(blank=True, null=True, max_length=500)
    read_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "read_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.email}: {self.title}"

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    def mark_read(self):
        if self.read_at is None:
            self.read_at = timezone.now()
            self.save(update_fields=["read_at"])


def notify(user, title, body, category="info", action_url=None):
    """
    Create a Notification row for a user. This is the package-level helper
    other apps use to emit notifications. Delivery channels (email, push,
    SMS) can be added later by hooking into post-save signals or by
    replacing this helper with a celery-enqueuing implementation.
    """
    return Notification.objects.create(
        user=user,
        title=title,
        body=body or "",
        category=category,
        action_url=action_url,
    )
