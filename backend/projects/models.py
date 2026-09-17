from django.conf import settings
from django.db import models
from django.utils.text import slugify


PROJECT_BUILD_MODES = [
    ("online", "Online"),
    ("physical", "Physical"),
    ("hybrid", "Hybrid"),
]

PROJECT_STATUS = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("under_review", "Under Review"),
    ("shortlisted", "Shortlisted"),
    ("winner", "Winner"),
    ("rejected", "Rejected"),
]


class Project(models.Model):
    team = models.OneToOneField(
        "teams.Team",
        on_delete=models.CASCADE,
        related_name="project",
    )
    hackathon = models.ForeignKey(
        "hackathons.Hackathon",
        on_delete=models.PROTECT,
        related_name="projects",
        db_index=True,
    )
    problem_statement = models.ForeignKey(
        "hackathons.ProblemStatement",
        on_delete=models.PROTECT,
        related_name="projects",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, db_index=True, blank=True)
    tagline = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    short_description = models.TextField(blank=True, default="")
    track = models.CharField(max_length=120, blank=True, null=True)
    build_mode = models.CharField(
        max_length=20, choices=PROJECT_BUILD_MODES, default="online"
    )
    technologies = models.JSONField(default=list, blank=True)
    repo_url = models.URLField(blank=True, null=True, max_length=500)
    demo_url = models.URLField(blank=True, null=True, max_length=500)
    demo_video_url = models.URLField(blank=True, null=True, max_length=500)
    status = models.CharField(
        max_length=20, choices=PROJECT_STATUS, default="draft", db_index=True
    )
    is_public = models.BooleanField(default=False, db_index=True)
    submitted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at", "-created_at"]
        unique_together = [("hackathon", "slug")]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "project"
            self.slug = f"{base}-{self.team_id}"
        super().save(*args, **kwargs)


ATTACHMENT_TYPES = [
    ("source_code", "Source Code"),
    ("deck", "Deck / Presentation"),
    ("demo_video", "Demo Video"),
    ("screenshot", "Screenshot"),
    ("report", "Report"),
    ("other", "Other"),
]


class ProjectAttachment(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="attachments", db_index=True
    )
    file = models.FileField(upload_to="projects/attachments/%Y/%m/")
    display_name = models.CharField(max_length=255)
    attachment_type = models.CharField(
        max_length=30, choices=ATTACHMENT_TYPES, default="other"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="project_attachments_uploaded",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.project.title} · {self.display_name}"

    @property
    def file_size(self):
        try:
            return self.file.size
        except Exception:
            return None

    @property
    def file_url(self):
        try:
            return self.file.url
        except Exception:
            return ""


INQUIRY_STATUS = [
    ("open", "Open"),
    ("answered", "Answered"),
    ("closed", "Closed"),
]


class ProjectInquiry(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_inquiries",
    )
    hackathon = models.ForeignKey(
        "hackathons.Hackathon",
        on_delete=models.CASCADE,
        related_name="inquiries",
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="inquiries",
        null=True,
        blank=True,
    )
    subject = models.CharField(max_length=180)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=INQUIRY_STATUS, default="open", db_index=True)
    admin_response = models.TextField(blank=True, default="")
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="project_inquiries_answered",
        null=True,
        blank=True,
    )
    responded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.subject} - {self.created_by.email}"
