from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F


class JudgeAssignment(models.Model):
    judge = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="judge_assignments",
    )
    hackathon = models.ForeignKey(
        "hackathons.Hackathon",
        on_delete=models.CASCADE,
        related_name="judge_assignments",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("judge", "hackathon")]

    def __str__(self) -> str:
        return f"{self.judge.email} @ {self.hackathon.title}"


class ProjectJudgeAssignment(models.Model):
    judge = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_assignments",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="judge_assignments",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("judge", "project")]

    def __str__(self) -> str:
        return f"{self.judge.email} → {self.project.title}"


class Score(models.Model):
    judge = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="scores",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="scores",
    )
    criterion = models.ForeignKey(
        "hackathons.JudgingCriterion",
        on_delete=models.CASCADE,
        related_name="scores",
    )
    value = models.IntegerField(default=0)
    comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("judge", "project", "criterion")]
        ordering = ["project", "criterion__order"]

    def __str__(self) -> str:
        return f"{self.judge.email} · {self.project.title} · {self.criterion.name}: {self.value}"

    def clean(self):
        if self.criterion_id and self.project_id:
            if self.criterion.hackathon_id != self.project.hackathon_id:
                raise ValidationError(
                    "Criterion must belong to the same hackathon as the project.",
                    code="CRITERION_HACKATHON_MISMATCH",
                )
        if self.value is not None:
            if self.value < 0:
                self.value = 0
            if self.criterion_id and self.value > self.criterion.max_score:
                self.value = self.criterion.max_score

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
