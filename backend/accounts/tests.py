from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class AccountWorkflowTests(TestCase):
	def setUp(self):
		self.client = APIClient()

	@patch("accounts.views.send_verification_email")
	def test_register_and_invalid_login_statuses(self, send_email):
		response = self.client.post("/api/v1/accounts/register/", {
			"email": "test@example.com",
			"password1": "Strong!Pass123",
			"password2": "Strong!Pass123",
		}, format="json")
		self.assertEqual(response.status_code, 201)
		send_email.assert_called_once()

		invalid = self.client.post("/api/v1/accounts/login/", {
			"email": "test@example.com",
			"password": "wrong-password",
		}, format="json")
		self.assertEqual(invalid.status_code, 401)

	def test_password_reset_request_is_non_enumerating(self):
		response = self.client.post("/api/v1/accounts/password-reset/", {
			"email": "missing@example.com",
		}, format="json")
		self.assertEqual(response.status_code, 200)
		self.assertIn("If an account exists", response.json()["detail"])
