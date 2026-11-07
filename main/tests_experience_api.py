import uuid

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Experience
from main.serializers import ExperienceSerializer


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class ExperienceAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "experience-session-test"
        cls.owner = User.objects.create_user(
            username="experience_owner", password=cls.password, is_superuser=True,
            email="owner-private@example.test",
        )
        cls.member = User.objects.create_user(username="experience_member", password=cls.password)
        cls.editor = User.objects.create_user(username="experience_editor", password=cls.password)
        cls.staff = User.objects.create_user(username="experience_staff", password=cls.password, is_staff=True)
        cls.editor.groups.add(Group.objects.create(name="Editor"))
        cls.experience = Experience.objects.create(
            title="Riset AI", description="Pengalaman riset", category="research",
            thumbnail="https://example.test/research.png",
        )
        cls.experience.starred_by.add(cls.owner)
        cls.list_url = reverse("api:experience-list")
        cls.detail_url = reverse("api:experience-detail", args=[cls.experience.pk])
        cls.star_url = reverse("api:experience-star", args=[cls.experience.pk])
        cls.payload = {
            "title": "Magang backend", "description": "Mengembangkan API",
            "category": "internship", "thumbnail": "", "ended_at": None,
        }

    def snapshot(self):
        return {
            "rows": list(Experience.objects.order_by("pk").values()),
            "stars": list(Experience.starred_by.through.objects.order_by("pk").values()),
        }

    def assert_denied_unchanged(self, method, url, payload=None, client=None, **extra):
        before = self.snapshot()
        response = getattr(client or self.client, method)(
            url, data=payload or {}, format="json", **extra,
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.snapshot(), before)
        return response

    def test_public_list_and_detail_have_explicit_safe_fields(self):
        expected = {
            "id", "title", "description", "category", "thumbnail", "started_at",
            "ended_at", "is_ongoing", "star_count", "is_starred",
        }
        for url in (self.list_url, self.detail_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                row = response.data[0] if isinstance(response.data, list) else response.data
                self.assertEqual(set(row), expected)
                self.assertEqual(row["id"], str(self.experience.pk))
                self.assertEqual(row["star_count"], 1)
                self.assertFalse(row["is_starred"])
                self.assertNotContains(response, self.owner.email)
                self.assertNotContains(response, self.owner.password)

    def test_public_head_and_options_do_not_change_data(self):
        before = self.snapshot()
        for url in (self.list_url, self.detail_url):
            self.assertEqual(self.client.head(url).status_code, 200)
            self.assertEqual(self.client.options(url).status_code, 200)
        self.assertEqual(self.snapshot(), before)

    def test_search_title_is_trimmed_case_insensitive_and_combines_category(self):
        Experience.objects.create(title="Riset komunitas", description="Relawan", category="volunteer")
        response = self.client.get(self.list_url, {"title": "  rIsEt  ", "category": "research"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id"] for row in response.data], [str(self.experience.pk)])

    def test_search_no_matches_returns_empty_list(self):
        response = self.client.get(self.list_url, {"title": "tidak-ada-data"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_invalid_category_filter_returns_400(self):
        response = self.client.get(self.list_url, {"category": "invalid-category"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("category", response.data)

    def test_guest_cannot_create_update_delete_or_star(self):
        for method, url, payload in (
            ("post", self.list_url, self.payload),
            ("put", self.detail_url, self.payload),
            ("patch", self.detail_url, {"title": "Forbidden"}),
            ("delete", self.detail_url, None),
            ("post", self.star_url, None),
        ):
            with self.subTest(method=method, url=url):
                self.assert_denied_unchanged(method, url, payload)

    def test_member_and_staff_cannot_manage_experience(self):
        for user in (self.member, self.staff):
            self.client.force_authenticate(user)
            for method, url, payload in (
                ("post", self.list_url, self.payload),
                ("put", self.detail_url, self.payload),
                ("patch", self.detail_url, {"title": "Forbidden"}),
                ("delete", self.detail_url, None),
            ):
                with self.subTest(user=user.username, method=method):
                    self.assert_denied_unchanged(method, url, payload)

    def test_editor_cannot_create_or_delete(self):
        self.client.force_authenticate(self.editor)
        self.assert_denied_unchanged("post", self.list_url, self.payload)
        self.assert_denied_unchanged("delete", self.detail_url)

    def test_editor_can_patch_and_put_existing_experience(self):
        self.client.force_authenticate(self.editor)
        partial = self.client.patch(self.detail_url, {"title": "  <b>Judul baru</b>  "}, format="json")
        self.assertEqual(partial.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Judul baru")
        self.assertEqual(self.experience.description, "Pengalaman riset")
        replaced = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(replaced.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.description, self.payload["description"])
        self.assertEqual(self.experience.category, "internship")
        self.assertEqual(list(self.experience.starred_by.all()), [self.owner])

    def test_owner_create_returns_201_sanitizes_and_persists(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "title": " <b>Magang</b> ", "description": " <p>Membangun API</p> ",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        created = Experience.objects.get(pk=response.data["id"])
        self.assertIsInstance(created.pk, uuid.UUID)
        self.assertEqual(created.title, "Magang")
        self.assertEqual(created.description, "Membangun API")
        self.assertEqual(Experience.objects.count(), 2)
        self.assertEqual(response.data["star_count"], 0)
        self.assertTrue(response.data["is_ongoing"])

    def test_owner_can_update_and_delete_with_204_empty_body(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(self.detail_url, {"description": "Revisi pemilik"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.description, "Revisi pemilik")
        deleted = self.client.delete(self.detail_url)
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(deleted.content, b"")
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())
        self.assertEqual(Experience.starred_by.through.objects.count(), 0)

    def test_invalid_text_category_url_and_date_do_not_create(self):
        self.client.force_authenticate(self.owner)
        for field, value in (
            ("title", " "), ("title", "<b></b>"), ("title", "x" * 256),
            ("description", "<p> </p>"), ("category", "unsupported"),
            ("thumbnail", "not-a-url"), ("thumbnail", "javascript:alert(1)"),
            ("thumbnail", "ftp://example.test/file.png"), ("ended_at", "not-a-date"),
        ):
            with self.subTest(field=field, value=value):
                before = self.snapshot()
                response = self.client.post(self.list_url, {**self.payload, field: value}, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
                self.assertEqual(self.snapshot(), before)

    def test_invalid_update_and_missing_required_put_fields_leave_database_unchanged(self):
        self.client.force_authenticate(self.editor)
        for method, payload in (
            ("patch", {"title": "<span> </span>"}),
            ("patch", {"ended_at": "invalid"}),
            ("put", {"title": "Description is missing"}),
        ):
            with self.subTest(method=method, payload=payload):
                before = self.snapshot()
                response = getattr(self.client, method)(self.detail_url, payload, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertEqual(self.snapshot(), before)

    def test_readonly_id_timestamps_and_star_fields_cannot_be_forged(self):
        self.client.force_authenticate(self.owner)
        original_started_at = self.experience.started_at
        response = self.client.patch(self.detail_url, {
            "id": str(uuid.uuid4()), "started_at": "2000-01-01T00:00:00Z", "is_ongoing": False,
            "starred_by": [self.member.pk], "star_count": 999, "is_starred": False,
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(response.data["id"], str(self.experience.pk))
        self.assertEqual(self.experience.started_at, original_started_at)
        self.assertEqual(list(self.experience.starred_by.all()), [self.owner])
        self.assertEqual(response.data["star_count"], 1)
        self.assertTrue(response.data["is_starred"])
        self.assertTrue(response.data["is_ongoing"])

    def test_nullable_thumbnail_and_end_date_are_supported(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(self.detail_url, {
            "thumbnail": None, "ended_at": "2025-01-01T00:00:00Z",
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["is_ongoing"])
        cleared = self.client.patch(self.detail_url, {"ended_at": None}, format="json")
        self.assertEqual(cleared.status_code, 200)
        self.assertTrue(cleared.data["is_ongoing"])

    def test_serializer_without_request_has_false_star_status(self):
        data = ExperienceSerializer(self.experience).data
        self.assertFalse(data["is_starred"])
        self.assertEqual(data["star_count"], 1)

    def test_missing_and_malformed_uuid_return_404_without_writes(self):
        self.client.force_authenticate(self.owner)
        detail = reverse("api:experience-detail", args=[uuid.uuid4()])
        star = detail + "star/"
        before = self.snapshot()
        for method, url, payload in (
            ("get", detail, {}), ("put", detail, self.payload),
            ("patch", detail, {"title": "Missing"}), ("delete", detail, {}),
            ("post", star, {}), ("get", self.list_url + "not-a-uuid/", {}),
        ):
            with self.subTest(method=method, url=url):
                response = getattr(self.client, method)(url, payload, format="json")
                self.assertEqual(response.status_code, 404)
                self.assertEqual(self.snapshot(), before)

    def test_all_authenticated_roles_toggle_only_their_own_star(self):
        self.experience.starred_by.clear()
        for user in (self.member, self.editor, self.owner):
            self.client.force_authenticate(user)
            with self.subTest(user=user.username):
                starred = self.client.post(self.star_url, {
                    "user_id": self.staff.pk, "starred_by": [self.staff.pk], "star_count": 99,
                }, format="json")
                self.assertEqual(starred.status_code, 200)
                self.assertTrue(starred.data["is_starred"])
                self.assertEqual(starred.data["star_count"], 1)
                self.assertEqual(list(self.experience.starred_by.all()), [user])
                unstarred = self.client.post(self.star_url, {}, format="json")
                self.assertEqual(unstarred.status_code, 200)
                self.assertFalse(unstarred.data["is_starred"])
                self.assertEqual(unstarred.data["star_count"], 0)
                self.assertFalse(self.experience.starred_by.exists())

    def test_star_status_changes_with_current_account_and_preserves_others(self):
        self.client.force_authenticate(self.member)
        self.assertFalse(self.client.get(self.detail_url).data["is_starred"])
        self.client.post(self.star_url)
        self.assertTrue(self.client.get(self.detail_url).data["is_starred"])
        self.assertEqual(self.client.get(self.detail_url).data["star_count"], 2)
        self.client.force_authenticate(self.editor)
        self.assertFalse(self.client.get(self.detail_url).data["is_starred"])
        self.assertTrue(self.experience.starred_by.filter(pk=self.owner.pk).exists())

    def test_star_get_is_not_a_write_endpoint(self):
        self.client.force_authenticate(self.member)
        before = self.snapshot()
        self.assertEqual(self.client.get(self.star_url).status_code, 405)
        self.assertEqual(self.snapshot(), before)

    def test_session_login_requires_csrf_for_owner_create_update_and_delete(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=self.owner.username, password=self.password))
        page = client.get(reverse("main:show_certifications"))
        self.assertEqual(page.status_code, 200)
        token = client.cookies[settings.CSRF_COOKIE_NAME].value
        for method, url, payload in (
            ("post", self.list_url, self.payload),
            ("patch", self.detail_url, {"title": "CSRF rejected"}),
            ("delete", self.detail_url, None),
        ):
            with self.subTest(method=method):
                self.assert_denied_unchanged(method, url, payload, client=client)
        accepted = client.post(self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(accepted.status_code, 201)
        self.assertTrue(Experience.objects.filter(pk=accepted.data["id"]).exists())

    def test_member_session_star_needs_csrf_and_cannot_be_replayed_after_logout(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=self.member.username, password=self.password))
        client.get(reverse("main:show_certifications"))
        token = client.cookies[settings.CSRF_COOKIE_NAME].value
        self.assert_denied_unchanged("post", self.star_url, client=client)
        accepted = client.post(self.star_url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(accepted.status_code, 200)
        self.assertTrue(self.experience.starred_by.filter(pk=self.member.pk).exists())
        client.logout()
        self.assert_denied_unchanged("post", self.star_url, client=client, HTTP_X_CSRFTOKEN=token)

    def test_revoked_editor_role_is_checked_again_in_existing_session(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=self.editor.username, password=self.password))
        client.get(reverse("main:show_certifications"))
        token = client.cookies[settings.CSRF_COOKIE_NAME].value
        accepted = client.patch(self.detail_url, {"title": "Allowed"}, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(accepted.status_code, 200)
        self.editor.groups.clear()
        self.assert_denied_unchanged(
            "patch", self.detail_url, {"title": "Forbidden"}, client=client, HTTP_X_CSRFTOKEN=token,
        )

    def test_browsable_api_is_available_to_public(self):
        response = self.client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "rest_framework")
