from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
import random
import string

User = get_user_model()


def _generate_invite_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    code = "".join(random.choices(alphabet, k=8))
    attempts = 0
    while Team.objects.filter(invite_code=code).exists() and attempts < 20:
        code = "".join(random.choices(alphabet, k=8))
        attempts += 1
    return code


class Team(models.Model):
    hackathon = models.ForeignKey(
        "hackathons.Hackathon",
        on_delete=models.PROTECT,
        related_name="teams",
        db_index=True,
    )
    name = models.CharField(max_length=120)
    tagline = models.CharField(max_length=255, blank=True, default="")
    track = models.CharField(max_length=120, blank=True, null=True)
    problem_statement = models.ForeignKey(
        "hackathons.ProblemStatement",
        on_delete=models.PROTECT,
        related_name="teams",
        null=True,
        blank=True,
    )
    invite_code = models.CharField(
        max_length=16, unique=True, default=_generate_invite_code, db_index=True
    )
    is_roster_locked = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_teams",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("hackathon", "name")]

    def __str__(self) -> str:
        return f"{self.name} · {self.hackathon.title}"

    @property
    def member_count(self) -> int:
        return self.memberships.count()

    @property
    def leader(self):
        return (
            self.memberships.filter(is_leader=True)
            .select_related("user")
            .first()
        )


TEAM_ROLE_CHOICES = [("leader", "Leader"), ("member", "Member")]


class TeamMembership(models.Model):
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team_memberships",
    )
    is_leader = models.BooleanField(default=False)
    role = models.CharField(
        max_length=20, choices=TEAM_ROLE_CHOICES, default="member"
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("team", "user")]
        ordering = ["-is_leader", "joined_at"]
        indexes = [
            models.Index(fields=["user"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} · {self.team.name}"

    def clean(self):
        hackathon = self.team.hackathon_id
        other = (
            TeamMembership.objects.filter(user=self.user, team__hackathon_id=hackathon)
            .exclude(pk=self.pk)
            .exclude(team_id=self.team_id)
            .exists()
        )
        if other:
            raise ValidationError(
                "A user cannot belong to multiple teams in the same hackathon.",
                code="DUPLICATE_HACKATHON_MEMBERSHIP",
            )

    def save(self, *args, **kwargs):
        if self.is_leader:
            self.role = "leader"
        elif not self.role:
            self.role = "member"
        self.full_clean()
        return super().save(*args, **kwargs)


TEAM_INVITE_STATUS = [
    ("pending", "Pending"),
    ("accepted", "Accepted"),
    ("revoked", "Revoked"),
]


class TeamInvite(models.Model):
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="invites"
    )
    email = models.EmailField(db_index=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="team_invites_sent",
    )
    status = models.CharField(
        max_length=20, choices=TEAM_INVITE_STATUS, default="pending"
    )
    code = models.CharField(max_length=16, default=_generate_invite_code, db_index=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.email} → {self.team.name}"

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at
