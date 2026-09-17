from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Hackathon, ProblemStatement

User = get_user_model()


class ParticipantEnrollmentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="participant",
            email="participant@example.com",
            password="Strong!Pass123",
            first_name="Test",
            last_name="Participant",
        )
        now = timezone.now()
        self.hackathon = Hackathon.objects.create(
            title="Enrollment Test",
            slug="enrollment-test",
            starts_at=now + timedelta(days=2),
            ends_at=now + timedelta(days=4),
            registration_opens_at=now - timedelta(days=1),
            registration_closes_at=now + timedelta(days=1),
        )
        self.problem = ProblemStatement.objects.create(
            hackathon=self.hackathon,
            title="Digital access",
            category="GovTech",
            summary="Improve access to a public service.",
            is_published=True,
        )
        self.client.force_authenticate(self.user)

    def test_profile_is_required_then_participant_can_enroll(self):
        payload = {
            "selected_problem": self.problem.id,
            "participation_preference": "need_team",
            "primary_role": "developer",
            "experience_level": "intermediate",
            "attendance_mode": "flexible",
            "motivation": "I want to build for KP.",
            "agreed_to_rules": True,
        }
        incomplete = self.client.post(
            f"/api/v1/hackathons/{self.hackathon.slug}/enrollment/",
            payload,
            format="json",
        )
        self.assertEqual(incomplete.status_code, 400)
        self.assertEqual(incomplete.json()["code"], "PROFILE_INCOMPLETE")

        profile = self.user.profile
        profile.phone = "+92 300 0000000"
        profile.institution = "Test University"
        profile.district = "Peshawar"
        profile.skills = ["React", "Python"]
        profile.save()

        enrolled = self.client.post(
            f"/api/v1/hackathons/{self.hackathon.slug}/enrollment/",
            payload,
            format="json",
        )
        self.assertEqual(enrolled.status_code, 201)
        self.assertEqual(enrolled.json()["selected_problem"], self.problem.id)

        mine = self.client.get("/api/v1/hackathons/enrollments/me/")
        self.assertEqual(mine.status_code, 200)
        self.assertEqual(len(mine.json()), 1)
