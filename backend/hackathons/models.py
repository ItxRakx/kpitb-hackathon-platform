from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Hackathon(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    tagline = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    cover_image_url = models.URLField(blank=True, null=True, max_length=500)
    rules_url = models.URLField(blank=True, null=True, max_length=500)

    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    registration_opens_at = models.DateTimeField()
    registration_closes_at = models.DateTimeField(db_index=True)

    team_min_size = models.PositiveSmallIntegerField(default=1)
    team_max_size = models.PositiveSmallIntegerField(default=6)
    is_active = models.BooleanField(default=True, db_index=True)
    results_published = models.BooleanField(default=False)
    require_roster_lock_to_register = models.BooleanField(default=True)
    require_participant_enrollment = models.BooleanField(default=True)
    prizes_text = models.TextField(blank=True, default="")
    tracks = models.JSONField(default=list, blank=True)
    rules = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-starts_at"]

    def __str__(self) -> str:
        return self.title

    @property
    def is_registration_open(self) -> bool:
        now = timezone.now()
        return (
            self.is_active
            and self.registration_opens_at <= now <= self.registration_closes_at
        )

    @property
    def is_ongoing(self) -> bool:
        now = timezone.now()
        return self.is_active and self.starts_at <= now <= self.ends_at

    @property
    def is_completed(self) -> bool:
        return self.ends_at < timezone.now()


PROBLEM_DIFFICULTY_CHOICES = [
    ("starter", "Starter"),
    ("intermediate", "Intermediate"),
    ("advanced", "Advanced"),
]


class ProblemStatement(models.Model):
    hackathon = models.ForeignKey(
        Hackathon, on_delete=models.CASCADE, related_name="problem_statements"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    category = models.CharField(max_length=120, db_index=True)
    summary = models.TextField()
    description = models.TextField(blank=True, default="")
    deliverables = models.TextField(blank=True, default="")
    difficulty = models.CharField(
        max_length=20, choices=PROBLEM_DIFFICULTY_CHOICES, default="intermediate"
    )
    is_published = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "title"]
        unique_together = [("hackathon", "slug")]

    def __str__(self) -> str:
        return f"{self.hackathon.title} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "challenge"
            candidate = base
            counter = 2
            while ProblemStatement.objects.filter(
                hackathon=self.hackathon, slug=candidate
            ).exclude(pk=self.pk).exists():
                candidate = f"{base}-{counter}"
                counter += 1
            self.slug = candidate
        super().save(*args, **kwargs)


ENROLLMENT_STATUS_CHOICES = [
    ("registered", "Registered"),
    ("approved", "Approved"),
    ("waitlist", "Waitlist"),
    ("cancelled", "Cancelled"),
]

PARTICIPATION_PREFERENCE_CHOICES = [
    ("create_team", "I want to lead a team"),
    ("join_team", "I already have a team"),
    ("need_team", "Help me find a team"),
    ("solo", "I plan to build solo"),
]

PARTICIPANT_ROLE_CHOICES = [
    ("developer", "Software developer"),
    ("data_ai", "Data / AI"),
    ("designer", "Designer / UX"),
    ("product", "Product / business"),
    ("domain_expert", "Domain expert"),
    ("student", "Student / learner"),
    ("other", "Other"),
]

EXPERIENCE_LEVEL_CHOICES = [
    ("beginner", "Beginner"),
    ("intermediate", "Intermediate"),
    ("advanced", "Advanced"),
]

ATTENDANCE_MODE_CHOICES = [
    ("onsite", "On-site"),
    ("online", "Online"),
    ("flexible", "Either / flexible"),
]


class ParticipantEnrollment(models.Model):
    hackathon = models.ForeignKey(
        Hackathon, on_delete=models.CASCADE, related_name="participant_enrollments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hackathon_enrollments",
    )
    selected_problem = models.ForeignKey(
        ProblemStatement,
        on_delete=models.SET_NULL,
        related_name="interested_participants",
        null=True,
        blank=True,
    )
    participation_preference = models.CharField(
        max_length=30, choices=PARTICIPATION_PREFERENCE_CHOICES
    )
    primary_role = models.CharField(max_length=30, choices=PARTICIPANT_ROLE_CHOICES)
    experience_level = models.CharField(
        max_length=20, choices=EXPERIENCE_LEVEL_CHOICES
    )
    attendance_mode = models.CharField(
        max_length=20, choices=ATTENDANCE_MODE_CHOICES, default="flexible"
    )
    motivation = models.TextField(blank=True, default="")
    agreed_to_rules = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20, choices=ENROLLMENT_STATUS_CHOICES, default="registered", db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("hackathon", "user")]

    def __str__(self) -> str:
        return f"{self.user.email} @ {self.hackathon.title}"


class JudgingCriterion(models.Model):
    hackathon = models.ForeignKey(
        Hackathon, on_delete=models.CASCADE, related_name="judging_criteria"
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    weight = models.FloatField(default=1.0)
    max_score = models.PositiveIntegerField(default=100)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("hackathon", "name")]
        ordering = ["order", "created_at"]

    def __str__(self) -> str:
        return f"{self.hackathon.title} · {self.name}"


REGISTRATION_STATUS = [
    ("confirmed", "Confirmed"),
    ("waitlist", "Waitlist"),
    ("cancelled", "Cancelled"),
]


class HackathonRegistration(models.Model):
    hackathon = models.ForeignKey(
        Hackathon,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    team = models.OneToOneField(
        "teams.Team",
        on_delete=models.CASCADE,
        related_name="hackathon_registration",
    )
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="team_registrations",
    )
    registered_at = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(
        max_length=20, choices=REGISTRATION_STATUS, default="confirmed"
    )

    class Meta:
        ordering = ["-registered_at"]
        unique_together = [("hackathon", "team")]

    def __str__(self) -> str:
        return f"{self.team.name} @ {self.hackathon.title}"
