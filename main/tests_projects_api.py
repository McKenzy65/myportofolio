from uuid import UUID, uuid4

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from main.models import Project


class ProjectCollectionTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("api:project-list")
        cls.owner = User.objects.create_superuser(username="owner")
        cls.member = User.objects.create_user(username="member")
        cls.payload = {
            "title": "Mobile Portfolio",
            "description": "Portfolio app for Android",
            "tech_stack": "Dart, Flutter",
            "project_url": "https://example.org/project",
        }

    def test_public_list_returns_existing_portfolio_projects_and_can_be_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Dione AI, AI-Powered Learning System", [p["title"] for p in response.data])
        for project in response.data:
            self.assertEqual(set(project), set(self.payload) | {"id", "project_image_url"})
            self.assertIsInstance(UUID(project["id"]), UUID)
        Project.objects.all().delete()
        self.assertEqual(self.client.get(self.url).data, [])

    def test_superuser_create_ignores_client_id_and_allows_empty_image(self):
        chosen_id = str(uuid4())
        self.client.force_authenticate(self.owner)
        response = self.client.post(self.url, {**self.payload, "id": chosen_id}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data["id"], chosen_id)
        self.assertEqual(response.data["project_image_url"], "")
        self.assertTrue(Project.objects.filter(pk=response.data["id"], **self.payload).exists())

    def test_ordinary_account_cannot_create_projects(self):
        self.client.force_authenticate(self.member)
        self.assertEqual(self.client.post(self.url, self.payload, format="json").status_code, 403)
        self.assertFalse(Project.objects.filter(title=self.payload["title"]).exists())

    def test_invalid_text_and_urls_return_field_errors(self):
        self.client.force_authenticate(self.owner)
        for field, invalid in (
            ("title", "   "), ("description", ""), ("tech_stack", "x" * 256),
            ("project_url", "invalid"), ("project_image_url", "ftp://example.org/image"),
        ):
            with self.subTest(field=field):
                response = self.client.post(self.url, {**self.payload, field: invalid}, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
