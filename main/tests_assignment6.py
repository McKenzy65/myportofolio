from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Certification, Experience


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class Assignment6IntegrationTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "assignment-session-password"
        cls.member = User.objects.create_user("a6_member", password=cls.password)
        cls.editor = User.objects.create_user("a6_editor", password=cls.password)
        cls.owner = User.objects.create_user("a6_owner", password=cls.password, is_superuser=True)
        cls.editor_group = Group.objects.create(name="Editor")
        cls.editor.groups.add(cls.editor_group)
        cls.cert = Certification.objects.create(title="Certificate", description="Description", year=2026)
        cls.cert.starred_by.add(cls.member)
        cls.experience = Experience.objects.create(title="Experience", description="Research", category="research")
        cls.experience.starred_by.add(cls.member)

    def certification_snapshot(self):
        return (
            list(Certification.objects.order_by("pk").values()),
            list(Certification.starred_by.through.objects.order_by("pk").values()),
        )

    def session_client(self, user):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=user.username, password=self.password))
        self.assertEqual(client.get(reverse("main:show_certifications")).status_code, 200)
        return client, client.cookies[settings.CSRF_COOKIE_NAME].value

    def test_edit_modal_is_available_only_to_owner_and_editor(self):
        for user in (None, self.member, self.editor, self.owner):
            with self.subTest(user=user):
                client = APIClient()
                if user:
                    client.force_login(user)
                page = client.get(reverse("main:show_certifications"))
                if user in (self.editor, self.owner):
                    self.assertContains(page, 'id="edit-certification-modal"')
                    self.assertContains(page, 'id="edit-certification-form"')
                else:
                    self.assertNotContains(page, 'id="edit-certification-modal"')
                if user != self.owner:
                    self.assertNotContains(page, 'id="add-certification-modal"')

    def test_editor_patch_with_real_session_csrf_and_validation(self):
        client, token = self.session_client(self.editor)
        url = reverse("api:certification-detail", args=[self.cert.pk])
        before = self.certification_snapshot()
        self.assertEqual(client.patch(url, {"title": "No token"}, format="json").status_code, 403)
        self.assertEqual(self.certification_snapshot(), before)
        response = client.patch(url, {"title": "<b>Updated</b>", "star_count": 99,
                                     "starred_by": [self.owner.pk]}, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.cert.refresh_from_db()
        self.assertEqual(self.cert.title, "Updated")
        self.assertEqual(self.cert.description, "Description")
        self.assertEqual(list(self.cert.starred_by.all()), [self.member])
        before = self.certification_snapshot()
        response = client.patch(url, {"title": "Must not persist", "description": "<b></b>"},
                                format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 400)
        self.assertIn("description", response.data)
        self.assertEqual(self.certification_snapshot(), before)

    def test_open_editor_session_cannot_write_after_group_revoked(self):
        client, token = self.session_client(self.editor)
        self.editor.groups.remove(self.editor_group)
        before = self.certification_snapshot()
        response = client.patch(reverse("api:certification-detail", args=[self.cert.pk]),
                                {"title": "Forbidden"}, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.certification_snapshot(), before)

    def test_legacy_routes_keep_same_role_boundaries_and_database(self):
        payload = {"title": "Forbidden", "description": "Changed", "year": 2020}
        for user in (None, self.member, self.editor):
            client = APIClient()
            if user:
                client.force_login(user)
            routes = [("main:create_certification", []), ("main:create_certification_ajax", []),
                      ("main:delete_certification", [self.cert.pk])]
            if user != self.editor:
                routes.append(("main:edit_certification", [self.cert.pk]))
            for name, args in routes:
                with self.subTest(user=user, route=name):
                    before = self.certification_snapshot()
                    response = client.post(reverse(name, args=args), payload)
                    self.assertEqual(response.status_code,
                                     302 if user is None and name != "main:create_certification_ajax" else 403)
                    self.assertEqual(self.certification_snapshot(), before)

    def test_legacy_experience_json_keeps_public_fields_without_account_ids(self):
        response = self.client.get(reverse("main:get_experiences_json"))
        self.assertEqual(response.status_code, 200)
        row = next(row for row in response.json() if row["pk"] == str(self.experience.pk))
        self.assertEqual(set(row["fields"]),
                         {"title", "description", "category", "thumbnail", "started_at", "ended_at"})

    def test_browsable_apis_and_existing_portfolio_sections_are_available(self):
        for name in ("api:certification-list", "api:experience-list"):
            response = self.client.get(reverse(name), HTTP_ACCEPT="text/html")
            self.assertEqual(response.status_code, 200)
            self.assertIn("text/html", response["Content-Type"])
            self.assertContains(response, "Django REST framework")
        page = self.client.get(reverse("main:show_main"))
        for section in ("profile", "skills", "education", "projects", "experience"):
            self.assertContains(page, f'id="{section}"')
