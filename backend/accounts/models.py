from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class ParticipantProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    institution = models.CharField(max_length=255, blank=True, null=True)
    district = models.CharField(max_length=120, blank=True, null=True, db_index=True)
    education_level = models.CharField(max_length=120, blank=True, null=True)
    skills = models.JSONField(default=list, blank=True)
    bio = models.TextField(blank=True, default="")
    portfolio_url = models.URLField(blank=True, null=True, max_length=500)
    github_url = models.URLField(blank=True, null=True, max_length=500)
    is_judge = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Profile: {self.user.email}"

    @property
    def is_complete(self) -> bool:
        return bool(
            self.user.first_name
            and self.user.last_name
            and self.phone
            and self.institution
            and self.district
            and self.skills
        )


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_participant_profile(
    sender, instance, created, **kwargs
):
    if created:
        ParticipantProfile.objects.get_or_create(user=instance)
    else:
        if not hasattr(instance, "profile"):
            ParticipantProfile.objects.get_or_create(user=instance)
