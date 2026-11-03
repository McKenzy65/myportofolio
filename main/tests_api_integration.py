from html.parser import HTMLParser

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Certification, Experience


class RenderedInputParser(HTMLParser):
    """Find real input elements rather than token strings inside JavaScript."""

    def __init__(self):
        super().__init__()
        self.inputs = []

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            self.inputs.append(dict(attrs))


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class CertificationSessionIntegrationTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        Certification.objects.all().delete()
        cls.password = "test-session-password"
        cls.owner = User.objects.create_user(
            username="integration_owner", password=cls.password, is_superuser=True,
        )
        cls.editor = User.objects.create_user(username="integration_editor", password=cls.password)
        cls.member = User.objects.create_user(username="integration_member", password=cls.password)
        cls.editor_group = Group.objects.get_or_create(name="Editor")[0]
        cls.editor.groups.add(cls.editor_group)
        cls.certification = Certification.objects.create(
            title="Integration entry", description="Existing description", year=2026,
        )
        cls.list_url = reverse("api:certification-list")
        cls.detail_url = reverse("api:certification-detail", args=[cls.certification.pk])
        cls.star_url = reverse("api:certification-star", args=[cls.certification.pk])
        cls.payload = {"title": "New entry", "description": "New description", "year": 2026}

    def logged_in_client(self, user):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=user.username, password=self.password))
        page = client.get(reverse("main:show_certifications"))
        self.assertEqual(page.status_code, 200)
        return client, client.cookies[settings.CSRF_COOKIE_NAME].value

    def test_password_login_csrf_and_logout_control_owner_creation(self):
        client, token = self.logged_in_client(self.owner)
        denied = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(Certification.objects.count(), 1)
        created = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(created.status_code, 201)
        self.assertEqual(Certification.objects.count(), 2)
        client.logout()
        denied_after_logout = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(denied_after_logout.status_code, 403)
        self.assertEqual(Certification.objects.count(), 2)

    def test_editor_session_can_update_but_cannot_create_or_delete(self):
        client, token = self.logged_in_client(self.editor)
        edited = client.patch(
            self.detail_url, {"title": "Edited by Editor"},
            format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(edited.status_code, 200)
        self.assertEqual(edited.data["title"], "Edited by Editor")
        self.assertEqual(client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        ).status_code, 403)
        self.assertEqual(client.delete(self.detail_url, HTTP_X_CSRFTOKEN=token).status_code, 403)
        self.assertEqual(Certification.objects.count(), 1)

    def test_revoking_editor_group_takes_effect_in_the_existing_session(self):
        client, token = self.logged_in_client(self.editor)
        self.assertEqual(client.patch(
            self.detail_url, {"title": "Allowed edit"},
            format="json", HTTP_X_CSRFTOKEN=token,
        ).status_code, 200)
        self.editor.groups.remove(self.editor_group)
        rejected = client.patch(
            self.detail_url, {"title": "Forbidden edit"},
            format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(rejected.status_code, 403)
        self.certification.refresh_from_db()
        self.assertEqual(self.certification.title, "Allowed edit")

    def test_member_session_can_star_but_cannot_manage_certifications(self):
        client, token = self.logged_in_client(self.member)
        response = client.post(self.star_url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_starred"])
        for method, url, payload in (
            ("post", self.list_url, self.payload),
            ("put", self.detail_url, self.payload),
            ("patch", self.detail_url, {"title": "Forbidden edit"}),
            ("delete", self.detail_url, {}),
        ):
            with self.subTest(method=method):
                denied = getattr(client, method)(
                    url, payload, format="json", HTTP_X_CSRFTOKEN=token,
                )
                self.assertEqual(denied.status_code, 403)
        self.certification.refresh_from_db()
        self.assertEqual(self.certification.title, "Integration entry")
        self.assertEqual(Certification.objects.count(), 1)

    def test_public_and_member_pages_render_a_real_csrf_token_without_create_modal(self):
        for user in (None, self.member, self.editor):
            with self.subTest(user=user):
                client = APIClient(enforce_csrf_checks=True)
                if user:
                    self.assertTrue(client.login(username=user.username, password=self.password))
                page = client.get(reverse("main:show_certifications"))
                self.assertEqual(page.status_code, 200)
                self.assertIn(settings.CSRF_COOKIE_NAME, client.cookies)
                parser = RenderedInputParser()
                parser.feed(page.content.decode())
                tokens = [field for field in parser.inputs if field.get("name") == "csrfmiddlewaretoken"]
                self.assertTrue(tokens, "CSRF input must be outside the inline script.")
                self.assertTrue(tokens[0].get("value"))
                self.assertNotContains(page, 'id="add-certification-modal"')

    def test_profile_projects_and_experience_remain_available(self):
        page = self.client.get(reverse("main:show_main"))
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "index.html")
        for section in ("profile", "skills", "education", "projects", "experience"):
            self.assertContains(page, f'id="{section}"')
        experience = Experience.objects.create(
            title="Existing experience flow", description="Preserved experience data",
            category="research",
        )
        response = self.client.get(reverse("main:get_experiences_json"), {"category": "research"})
        self.assertEqual(response.status_code, 200)
        rows = {row["pk"]: row["fields"] for row in response.json()}
        self.assertIn(str(experience.pk), rows)
        self.assertEqual(rows[str(experience.pk)]["title"], experience.title)
