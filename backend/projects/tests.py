from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from hackathons.models import Hackathon, HackathonRegistration
from teams.models import Team, TeamMembership
from .models import Project
from .models import ProjectInquiry

User = get_user_model()


class ProjectPrivacyTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create_user(username="builder", email="builder@example.com", password="Strong!Pass123")
		self.hackathon = Hackathon.objects.create(
			title="Test Hackathon", slug="test-hackathon",
			starts_at=timezone.now() + timedelta(days=1), ends_at=timezone.now() + timedelta(days=2),
			registration_opens_at=timezone.now() - timedelta(days=1), registration_closes_at=timezone.now() + timedelta(days=1),
		)
		self.team = Team.objects.create(hackathon=self.hackathon, name="Test Team", created_by=self.user)
		TeamMembership.objects.create(team=self.team, user=self.user, is_leader=True, role="leader")
		HackathonRegistration.objects.create(hackathon=self.hackathon, team=self.team, registered_by=self.user)
		self.project = Project.objects.create(team=self.team, hackathon=self.hackathon, title="Private Project")

	def test_private_project_is_hidden_from_public_gallery_but_visible_to_team(self):
		public = self.client.get("/api/v1/projects/")
		self.assertEqual(public.status_code, 200)
		self.assertEqual(len(public.json()["results"]), 0)

		self.client.force_authenticate(self.user)
		detail = self.client.get(f"/api/v1/projects/{self.project.slug}/")
		self.assertEqual(detail.status_code, 200)


class ProjectInquiryTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create_user(username="asker", email="asker@example.com", password="Strong!Pass123")
		self.staff = User.objects.create_superuser(username="organizer", email="organizer@example.com", password="Strong!Pass123")
		now = timezone.now()
		self.hackathon = Hackathon.objects.create(
			title="Help Test", slug="help-test",
			starts_at=now + timedelta(days=1), ends_at=now + timedelta(days=2),
			registration_opens_at=now - timedelta(days=1), registration_closes_at=now + timedelta(days=1),
		)

	def test_participant_question_and_staff_response(self):
		self.client.force_authenticate(self.user)
		created = self.client.post("/api/v1/projects/inquiries/", {
			"hackathon": self.hackathon.id,
			"subject": "Submission format",
			"message": "Can we attach a PDF proposal?",
		}, format="json")
		self.assertEqual(created.status_code, 201)
		inquiry_id = created.json()["id"]

		self.client.force_authenticate(self.staff)
		answered = self.client.patch(f"/api/v1/projects/inquiries/{inquiry_id}/", {
			"admin_response": "Yes, attach it to the proposal.",
			"status": "answered",
		}, format="json")
		self.assertEqual(answered.status_code, 200)
		self.assertEqual(answered.json()["status"], "answered")
		self.assertEqual(ProjectInquiry.objects.get(id=inquiry_id).responded_by, self.staff)
