from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from main.models import Certification, Project


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class MobileAuthTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.credentials = {"username": "owner", "password": "only-for-the-test-database"}
        cls.owner = User.objects.create_superuser(**cls.credentials)
        cls.member = User.objects.create_user(username="member")
        cls.token_url = reverse("api:api_token_auth")
        cls.logout_url = reverse("api:api_logout")
        cls.projects_url = reverse("api:project-list")
        cls.payload = {
            "title": "Mobile project", "description": "Integration test",
            "tech_stack": "Flutter", "project_url": "https://example.org/mobile",
        }

    def test_mobile_session_can_create_project_and_revoke_only_its_own_token(self):
        other = Token.objects.create(user=self.member)
        client = APIClient(enforce_csrf_checks=True)
        login = client.post(self.token_url, self.credentials, format="json")
        self.assertEqual(login.status_code, 200)
        self.assertEqual(set(login.data), {"token"})
        client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        self.assertEqual(client.post(self.projects_url, self.payload, format="json").status_code, 201)
        response = client.post(self.logout_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertEqual(client.post(self.projects_url, self.payload, format="json").status_code, 401)
        self.assertEqual(client.post(self.logout_url).status_code, 401)
        self.assertTrue(Token.objects.filter(pk=other.pk).exists())

    def test_certification_token_create_public_detail_and_revocation(self):
        url = reverse("api:certification-list")
        payload = {"title": "Mobile QA", "description": "Portfolio", "year": 2026}
        client = APIClient(enforce_csrf_checks=True)
        self.assertEqual(client.get(url).status_code, 200)
        self.assertEqual(client.post(url, payload, format="json").status_code, 401)
        member_token = Token.objects.create(user=self.member)
        client.credentials(HTTP_AUTHORIZATION=f"Token {member_token.key}")
        self.assertEqual(client.post(url, payload, format="json").status_code, 403)

        token = Token.objects.create(user=self.owner)
        client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        created = client.post(url, payload, format="json")
        self.assertEqual(created.status_code, 201)
        detail_url = reverse("api:certification-detail", args=[created.data["id"]])
        self.assertEqual(APIClient().get(detail_url).data, created.data)
        token.delete()
        rejected = client.post(url, payload, format="json")
        self.assertEqual(rejected.status_code, 401)
        self.assertEqual(rejected["WWW-Authenticate"], "Token")
        self.assertEqual(Certification.objects.filter(title="Mobile QA").count(), 1)

    def test_wrong_password_anonymous_and_regular_token(self):
        invalid = {**self.credentials, "password": "incorrect"}
        self.assertEqual(self.client.post(self.token_url, invalid, format="json").status_code, 400)
        self.assertFalse(Token.objects.filter(user=self.owner).exists())
        self.assertEqual(self.client.post(self.logout_url).status_code, 401)
        self.assertEqual(self.client.post(self.projects_url, self.payload, format="json").status_code, 401)
        token = Token.objects.create(user=self.member)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.assertEqual(self.client.post(self.projects_url, self.payload, format="json").status_code, 403)
        self.assertFalse(Project.objects.filter(title=self.payload["title"]).exists())

    def test_browser_session_requires_csrf_and_cannot_revoke_another_client_token(self):
        token = Token.objects.create(user=self.owner)
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post(self.projects_url, self.payload, format="json").status_code, 403)
        self.assertEqual(client.post(self.logout_url).status_code, 403)
        client.get(reverse("main:show_certifications"))
        csrf = client.cookies["csrftoken"].value
        self.assertEqual(client.post(self.logout_url, HTTP_X_CSRFTOKEN=csrf).status_code, 204)
        self.assertTrue(Token.objects.filter(pk=token.pk).exists())

    @override_settings(CORS_ALLOWED_ORIGINS=["http://localhost:7357"], CORS_ALLOWED_ORIGIN_REGEXES=[])
    def test_hosted_api_only_allows_the_configured_demo_origin(self):
        url = reverse("api:certification-list")
        for origin, allowed in [
            ("http://localhost:7357", True),
            ("http://localhost:7358", False),
            ("https://outside.example", False),
        ]:
            with self.subTest(origin=origin):
                response = self.client.options(
                    url, HTTP_ORIGIN=origin, HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
                    HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization,content-type",
                )
                self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), origin if allowed else None)
                self.assertNotIn("Access-Control-Allow-Credentials", response.headers)

    def test_local_web_origin_and_emulator_host(self):
        origin = "http://localhost:57226"
        preflight = self.client.options(
            self.projects_url, HTTP_ORIGIN=origin,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization, content-type",
        )
        self.assertEqual(preflight["Access-Control-Allow-Origin"], origin)
        self.assertIn("authorization", preflight["Access-Control-Allow-Headers"])
        self.assertEqual(self.client.get(self.projects_url, HTTP_HOST="10.0.2.2:8000").status_code, 200)
        denied_origin = self.client.get(self.projects_url, HTTP_ORIGIN="https://outside.example")
        self.assertNotIn("Access-Control-Allow-Origin", denied_origin)
