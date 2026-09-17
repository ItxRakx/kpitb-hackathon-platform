from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from hackathons.models import Hackathon, ParticipantEnrollment, ProblemStatement

User = get_user_model()


class TeamRegistrationFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.lead = User.objects.create_user(
            username="lead", email="lead@example.com", password="Strong!Pass123"
        )
        self.member = User.objects.create_user(
            username="member", email="member@example.com", password="Strong!Pass123"
        )
        self.extra = User.objects.create_user(
            username="extra", email="extra@example.com", password="Strong!Pass123"
        )
        now = timezone.now()
        self.hackathon = Hackathon.objects.create(
            title="KP Challenge",
            slug="kp-challenge",
            starts_at=now + timedelta(days=2),
            ends_at=now + timedelta(days=4),
            registration_opens_at=now - timedelta(days=1),
            registration_closes_at=now + timedelta(days=1),
            team_min_size=2,
            team_max_size=2,
        )
        self.problem = ProblemStatement.objects.create(
            hackathon=self.hackathon,
            title="Better citizen services",
            category="GovTech",
            summary="Reduce time spent accessing a public service.",
            is_published=True,
        )
        for user, preference in (
            (self.lead, "create_team"),
            (self.member, "join_team"),
            (self.extra, "need_team"),
        ):
            profile = user.profile
            profile.phone = "+92 300 0000000"
            profile.institution = "Test University"
            profile.district = "Peshawar"
            profile.skills = ["Python"]
            profile.save()
            ParticipantEnrollment.objects.create(
                hackathon=self.hackathon,
                user=user,
                selected_problem=self.problem,
                participation_preference=preference,
                primary_role="developer",
                experience_level="intermediate",
                attendance_mode="flexible",
                agreed_to_rules=True,
            )

    def test_problem_team_capacity_lock_and_registration_flow(self):
        public_problems = self.client.get("/api/v1/hackathons/problems/")
        self.assertEqual(public_problems.status_code, 200)
        self.assertEqual(public_problems.json()["results"][0]["id"], self.problem.id)

        self.client.force_authenticate(self.lead)
        created = self.client.post(
            "/api/v1/teams/",
            {
                "name": "Frontier Builders",
                "hackathon": self.hackathon.id,
                "problem_statement": self.problem.id,
            },
            format="json",
        )
        self.assertEqual(created.status_code, 201)
        team_id = created.json()["id"]
        detail = self.client.get(f"/api/v1/teams/{team_id}/").json()
        invite_code = detail["invite_code"]
        self.assertTrue(detail["is_leader"])

        self.client.force_authenticate(self.member)
        joined = self.client.post(
            "/api/v1/teams/join-by-code/", {"invite_code": invite_code}, format="json"
        )
        self.assertEqual(joined.status_code, 201)

        self.client.force_authenticate(self.extra)
        full = self.client.post(
            "/api/v1/teams/join-by-code/", {"invite_code": invite_code}, format="json"
        )
        self.assertEqual(full.status_code, 409)

        self.client.force_authenticate(self.lead)
        locked = self.client.post(f"/api/v1/teams/{team_id}/lock-roster/", format="json")
        self.assertEqual(locked.status_code, 200)
        registered = self.client.post(
            f"/api/v1/hackathons/{self.hackathon.slug}/register-team/",
            {"team_id": team_id},
            format="json",
        )
        self.assertEqual(registered.status_code, 201)
