from django.conf import settings
from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Certification


class CertificationListAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = {
            "member": User.objects.create_user(
                username="api_member", email="member-private@example.com",
            ),
            "staff": User.objects.create_user(username="api_staff", is_staff=True),
            "editor": User.objects.create_user(username="api_editor"),
            "owner": User.objects.create_user(
                username="api_owner", is_superuser=True, is_staff=True,
            ),
        }
        cls.users["editor"].groups.add(Group.objects.get_or_create(name="Editor")[0])

    def setUp(self):
        # Data migrations may seed portfolio entries; each test needs known data.
        Certification.objects.all().delete()
        self.alpha = Certification.objects.create(
            title="Alpha Cloud", description="Cloud certification",
            year=2024, is_highlight=True,
        )
        self.beta = Certification.objects.create(
            title="Beta Security", description="Security certification", year=2025,
        )
        self.gamma = Certification.objects.create(
            title="Gamma Cloud", description="Advanced cloud certification",
            year=2025, is_highlight=True,
        )
        self.delta = Certification.objects.create(
            title="Delta Design", description="Design certification", year=2023,
        )
        self.alpha.starred_by.add(
            self.users["member"], self.users["editor"], self.users["owner"],
        )
        self.beta.starred_by.add(self.users["owner"])
        self.gamma.starred_by.add(self.users["member"], self.users["editor"])
        self.url = reverse("api:certification-list")
        self.payload = {
            "title": "New Certification",
            "description": "A new certification description",
            "year": 2026,
        }

    def client_for(self, role, enforce_csrf=False):
        client = APIClient(enforce_csrf_checks=enforce_csrf)
        if role is not None:
            client.force_login(self.users[role])
        return client

    def response_ids(self, response):
        self.assertEqual(response.status_code, 200)
        return [row["id"] for row in response.data]

    def test_public_list_uses_flat_public_serializer_fields(self):
        self.assertEqual(self.url, "/api/v1/certifications/")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 4)
        expected_fields = {
            "id", "title", "description", "year", "is_highlight",
            "star_count", "is_starred", "starred_by_names",
        }
        for row in response.data:
            self.assertEqual(set(row), expected_fields)
            self.assertFalse(row["is_starred"])
        self.assertNotContains(response, "member-private@example.com")

    def test_empty_list_returns_an_empty_array(self):
        Certification.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_safe_methods_do_not_modify_certifications_or_stars(self):
        before_rows = list(Certification.objects.order_by("pk").values())
        through = Certification.starred_by.through
        before_stars = list(through.objects.order_by("pk").values())
        for method in ("get", "head", "options"):
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    list(Certification.objects.order_by("pk").values()), before_rows,
                )
                self.assertEqual(list(through.objects.order_by("pk").values()), before_stars)

    def test_star_fields_use_the_current_session_without_exposing_accounts(self):
        for role, starred_ids in (
            (None, set()),
            ("member", {self.alpha.pk, self.gamma.pk}),
            ("owner", {self.alpha.pk, self.beta.pk}),
        ):
            with self.subTest(role=role):
                response = self.client_for(role).get(self.url)
                self.assertEqual(response.status_code, 200)
                rows = {row["id"]: row for row in response.data}
                self.assertEqual(rows[self.alpha.pk]["star_count"], 3)
                self.assertEqual(rows[self.gamma.pk]["star_count"], 2)
                self.assertEqual(rows[self.delta.pk]["star_count"], 0)
                self.assertEqual(
                    set(rows[self.alpha.pk]["starred_by_names"].split(", ")),
                    {"api_member", "api_editor", "api_owner"},
                )
                self.assertEqual(
                    {pk for pk, row in rows.items() if row["is_starred"]}, starred_ids,
                )
                for row in rows.values():
                    self.assertNotIn("starred_by", row)
                    self.assertNotIn("email", row)
                    self.assertNotIn("password", row)

    def test_title_filter_trims_and_matches_case_insensitively(self):
        for query, expected in (
            ("  cLoUd  ", [self.gamma.pk, self.alpha.pk]),
            ("missing title", []),
            ("   ", [self.gamma.pk, self.beta.pk, self.alpha.pk, self.delta.pk]),
        ):
            with self.subTest(query=query):
                response = self.client.get(self.url, {"title": query})
                self.assertEqual(self.response_ids(response), expected)

    def test_year_highlight_and_title_filters_can_be_combined(self):
        for params, expected in (
            ({"year": "2025"}, [self.gamma.pk, self.beta.pk]),
            ({"highlight": "1"}, [self.gamma.pk, self.alpha.pk]),
            ({"title": "cloud", "year": "2025", "highlight": "1"}, [self.gamma.pk]),
            ({"year": "0"}, []),
            ({"year": "2147483647"}, []),
        ):
            with self.subTest(params=params):
                self.assertEqual(self.response_ids(self.client.get(self.url, params)), expected)

    def test_invalid_year_filters_return_400(self):
        for year in ("unknown", "2025.5", "-1", "2147483648"):
            with self.subTest(year=year):
                response = self.client.get(self.url, {"year": year})
                self.assertEqual(response.status_code, 400)
        self.assertEqual(Certification.objects.count(), 4)

    def test_favorites_filter_requires_login_and_combines_with_other_filters(self):
        self.assertEqual(self.client.get(self.url, {"starred": "1"}).status_code, 403)
        client = self.client_for("member")
        self.assertEqual(
            self.response_ids(client.get(self.url, {"starred": "1"})),
            [self.gamma.pk, self.alpha.pk],
        )
        self.assertEqual(
            self.response_ids(client.get(self.url, {
                "starred": "1", "title": "cloud", "year": "2024", "highlight": "1",
            })),
            [self.alpha.pk],
        )

    def test_sort_options_and_unknown_sort_have_deterministic_order(self):
        expected_orders = {
            "newest": [self.gamma.pk, self.beta.pk, self.alpha.pk, self.delta.pk],
            "oldest": [self.delta.pk, self.alpha.pk, self.beta.pk, self.gamma.pk],
            "title": [self.alpha.pk, self.beta.pk, self.delta.pk, self.gamma.pk],
            "popular": [self.alpha.pk, self.gamma.pk, self.beta.pk, self.delta.pk],
            "unknown": [self.gamma.pk, self.beta.pk, self.alpha.pk, self.delta.pk],
        }
        for sort, expected in expected_orders.items():
            with self.subTest(sort=sort):
                self.assertEqual(
                    self.response_ids(self.client.get(self.url, {"sort": sort})), expected,
                )

    def test_popular_favorites_keep_global_star_counts(self):
        response = self.client_for("member").get(self.url, {
            "starred": "1", "sort": "popular",
        })
        self.assertEqual(self.response_ids(response), [self.alpha.pk, self.gamma.pk])
        self.assertEqual([row["star_count"] for row in response.data], [3, 2])

    def test_owner_can_create_json_and_receives_saved_normalized_data(self):
        payload = {
            **self.payload,
            "title": "  <b>New Certification</b>  ",
            "description": "  <p>A new certification description</p>  ",
        }
        response = self.client_for("owner").post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 201)
        created = Certification.objects.get(pk=response.data["id"])
        self.assertEqual(Certification.objects.count(), 5)
        self.assertEqual(created.title, self.payload["title"])
        self.assertEqual(created.description, self.payload["description"])
        self.assertEqual(created.year, 2026)
        self.assertFalse(created.is_highlight)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_owner_can_create_with_form_data(self):
        response = self.client_for("owner").post(self.url, {
            **self.payload, "year": "2026", "is_highlight": "true",
        }, format="multipart")
        self.assertEqual(response.status_code, 201)
        created = Certification.objects.get(pk=response.data["id"])
        self.assertTrue(created.is_highlight)
        self.assertEqual(created.year, 2026)

    def test_invalid_creates_return_field_errors_without_saving(self):
        client = self.client_for("owner")
        for payload, field in (
            ({}, "title"),
            ({**self.payload, "title": "<b></b>"}, "title"),
            ({**self.payload, "description": "<p> </p>"}, "description"),
            ({**self.payload, "title": "x" * 256}, "title"),
            ({**self.payload, "year": -1}, "year"),
            ({**self.payload, "year": "not a year"}, "year"),
        ):
            with self.subTest(payload=payload):
                response = client.post(self.url, payload, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
                self.assertEqual(Certification.objects.count(), 4)

    def test_client_cannot_set_ids_or_forge_star_information(self):
        response = self.client_for("owner").post(self.url, {
            **self.payload,
            "id": self.alpha.pk,
            "star_count": 999,
            "is_starred": True,
            "starred_by_names": "forged account",
            "starred_by": [self.users["member"].pk],
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data["id"], self.alpha.pk)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")
        self.assertFalse(Certification.objects.get(pk=response.data["id"]).starred_by.exists())
        self.alpha.refresh_from_db()
        self.assertEqual(self.alpha.title, "Alpha Cloud")

    def test_only_owner_can_create_even_when_other_roles_are_authenticated(self):
        for role in (None, "member", "staff", "editor"):
            with self.subTest(role=role):
                response = self.client_for(role).post(self.url, self.payload, format="json")
                self.assertEqual(response.status_code, 403)
                self.assertEqual(Certification.objects.count(), 4)

    def test_owner_session_create_requires_a_valid_csrf_token(self):
        client = self.client_for("owner", enforce_csrf=True)
        login_response = client.get(reverse("rest_framework:login"))
        self.assertEqual(login_response.status_code, 200)
        token = client.cookies[settings.CSRF_COOKIE_NAME].value
        denied = client.post(self.url, self.payload, format="json")
        self.assertEqual(denied.status_code, 403)
        self.assertIn("CSRF", str(denied.data["detail"]))
        self.assertEqual(Certification.objects.count(), 4)
        allowed = client.post(
            self.url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(allowed.status_code, 201)
        self.assertEqual(Certification.objects.count(), 5)

    def test_malformed_json_returns_400_without_saving(self):
        response = self.client_for("owner").post(
            self.url, '{"title":', content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Certification.objects.count(), 4)

    def test_list_endpoint_rejects_update_and_delete_methods(self):
        client = self.client_for("owner")
        for method in ("put", "patch", "delete"):
            with self.subTest(method=method):
                response = getattr(client, method)(self.url, self.payload, format="json")
                self.assertEqual(response.status_code, 405)
                self.assertEqual(Certification.objects.count(), 4)

    def test_legacy_certification_endpoint_keeps_its_existing_response_shape(self):
        response = self.client.get(reverse("main:get_certifications_json"))
        self.assertEqual(response.status_code, 200)
        rows = response.json()
        self.assertEqual(len(rows), 4)
        for row in rows:
            self.assertEqual(set(row), {"model", "pk", "fields"})
            self.assertEqual(row["model"], "main.certification")
            self.assertIn("title", row["fields"])
            self.assertIn("star_count", row["fields"])

    def test_browsable_api_renders_html(self):
        response = self.client_for("owner").get(self.url, HTTP_ACCEPT="text/html")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/html"))
        self.assertContains(response, "Alpha Cloud")
        self.assertContains(response, "<html")


class CertificationDetailAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = {
            "member": User.objects.create_user(
                username="detail_member", email="detail-private@example.com",
            ),
            "staff": User.objects.create_user(username="detail_staff", is_staff=True),
            "editor": User.objects.create_user(username="detail_editor"),
            "owner": User.objects.create_user(
                username="detail_owner", is_superuser=True, is_staff=True,
            ),
        }
        cls.users["editor"].groups.add(Group.objects.get_or_create(name="Editor")[0])

    def setUp(self):
        Certification.objects.all().delete()
        self.target = Certification.objects.create(
            title="Target Certification", description="Original description",
            year=2024, is_highlight=True,
        )
        self.other = Certification.objects.create(
            title="Other Certification", description="Keep this entry", year=2023,
        )
        self.target.starred_by.add(self.users["member"], self.users["editor"])
        self.other.starred_by.add(self.users["owner"])
        self.url = reverse("api:certification-detail", args=[self.target.pk])
        self.payload = {
            "title": "Updated Certification",
            "description": "Updated description",
            "year": 2026,
            "is_highlight": False,
        }

    def client_for(self, role, enforce_csrf=False):
        client = APIClient(enforce_csrf_checks=enforce_csrf)
        if role is not None:
            client.force_login(self.users[role])
        return client

    def saved_state(self):
        return (
            list(Certification.objects.order_by("pk").values()),
            list(Certification.starred_by.through.objects.order_by("pk").values()),
        )

    def csrf_token(self, client):
        response = client.get(reverse("rest_framework:login"))
        self.assertEqual(response.status_code, 200)
        return client.cookies[settings.CSRF_COOKIE_NAME].value

    def test_detail_returns_public_fields_and_session_specific_stars(self):
        self.assertEqual(self.url, f"/api/v1/certifications/{self.target.pk}/")
        for role, is_starred in ((None, False), ("member", True), ("owner", False)):
            with self.subTest(role=role):
                response = self.client_for(role).get(self.url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(set(response.data), {
                    "id", "title", "description", "year", "is_highlight",
                    "star_count", "is_starred", "starred_by_names",
                })
                self.assertEqual(response.data["id"], self.target.pk)
                self.assertEqual(response.data["title"], self.target.title)
                self.assertEqual(response.data["star_count"], 2)
                self.assertEqual(response.data["is_starred"], is_starred)
                self.assertEqual(
                    set(response.data["starred_by_names"].split(", ")),
                    {"detail_member", "detail_editor"},
                )
                self.assertNotContains(response, "detail-private@example.com")

    def test_safe_detail_methods_are_public_and_do_not_change_data(self):
        before = self.saved_state()
        for role in (None, *self.users):
            client = self.client_for(role)
            for method in ("get", "head", "options"):
                with self.subTest(role=role, method=method):
                    self.assertEqual(getattr(client, method)(self.url).status_code, 200)
                    self.assertEqual(self.saved_state(), before)

    def test_missing_objects_and_malformed_identifiers_return_404(self):
        before = self.saved_state()
        missing_url = reverse("api:certification-detail", args=[self.other.pk + 1000])
        self.assertEqual(self.client.get(missing_url).status_code, 404)
        owner = self.client_for("owner")
        for method in ("put", "patch", "delete"):
            with self.subTest(method=method):
                response = getattr(owner, method)(missing_url, self.payload, format="json")
                self.assertEqual(response.status_code, 404)
        for identifier in ("abc", "-1", "1.5"):
            with self.subTest(identifier=identifier):
                self.assertEqual(
                    self.client.get(f"/api/v1/certifications/{identifier}/").status_code, 404,
                )
        self.assertEqual(self.saved_state(), before)

    def test_owner_and_editor_can_update_using_put_and_patch(self):
        for role in ("owner", "editor"):
            client = self.client_for(role)
            for method in ("put", "patch"):
                with self.subTest(role=role, method=method):
                    payload = {**self.payload, "title": f"<b>{role} {method}</b>"}
                    response = getattr(client, method)(self.url, payload, format="json")
                    self.assertEqual(response.status_code, 200)
                    self.target.refresh_from_db()
                    self.assertEqual(self.target.title, f"{role} {method}")
                    self.assertEqual(self.target.description, self.payload["description"])
                    self.assertEqual(self.target.year, 2026)
                    self.assertFalse(self.target.is_highlight)
                    self.assertEqual(response.data["id"], self.target.pk)
                    self.assertEqual(response.data["star_count"], 2)
                    self.assertEqual(response.data["is_starred"], role == "editor")
                    self.assertEqual(Certification.objects.count(), 2)

    def test_other_roles_cannot_update_even_with_valid_payloads(self):
        before = self.saved_state()
        for role in (None, "member", "staff"):
            client = self.client_for(role)
            for method in ("put", "patch"):
                with self.subTest(role=role, method=method):
                    response = getattr(client, method)(self.url, self.payload, format="json")
                    self.assertEqual(response.status_code, 403)
                    self.assertEqual(self.saved_state(), before)

    def test_owner_delete_removes_only_target_and_its_star_relations(self):
        other_before = Certification.objects.values().get(pk=self.other.pk)
        response = self.client_for("owner").delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertEqual(list(Certification.objects.values_list("pk", flat=True)), [self.other.pk])
        self.assertEqual(Certification.objects.values().get(pk=self.other.pk), other_before)
        self.assertEqual(
            list(Certification.starred_by.through.objects.values_list(
                "certification_id", "user_id",
            )),
            [(self.other.pk, self.users["owner"].pk)],
        )
        self.assertTrue(User.objects.filter(pk=self.users["member"].pk).exists())

    def test_editor_and_other_nonowners_cannot_delete(self):
        before = self.saved_state()
        for role in (None, "member", "staff", "editor"):
            with self.subTest(role=role):
                self.assertEqual(self.client_for(role).delete(self.url).status_code, 403)
                self.assertEqual(self.saved_state(), before)

    def test_put_requires_title_description_and_year_without_partial_save(self):
        before = self.saved_state()
        client = self.client_for("owner")
        for field in ("title", "description", "year"):
            with self.subTest(field=field):
                payload = {key: value for key, value in self.payload.items() if key != field}
                response = client.put(self.url, payload, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
                self.assertEqual(self.saved_state(), before)

    def test_patch_can_change_only_title_and_preserves_omitted_fields(self):
        response = self.client_for("editor").patch(
            self.url, {"title": "  <b>Renamed</b>  "}, format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.target.refresh_from_db()
        self.assertEqual(self.target.title, "Renamed")
        self.assertEqual(self.target.description, "Original description")
        self.assertEqual(self.target.year, 2024)
        self.assertTrue(self.target.is_highlight)
        self.assertEqual(self.target.starred_by.count(), 2)
        self.assertEqual(response.data["description"], "Original description")

    def test_invalid_updates_return_field_errors_without_mutation(self):
        before = self.saved_state()
        client = self.client_for("owner")
        for method in ("put", "patch"):
            for field, value in (
                ("title", "<b></b>"), ("description", "<p> </p>"),
                ("title", "x" * 256), ("year", -1), ("year", "not a year"),
            ):
                with self.subTest(method=method, field=field, value=value):
                    response = getattr(client, method)(
                        self.url, {**self.payload, field: value}, format="json",
                    )
                    self.assertEqual(response.status_code, 400)
                    self.assertIn(field, response.data)
                    self.assertEqual(self.saved_state(), before)

    def test_updates_cannot_change_identity_or_forge_star_memberships(self):
        other_before = Certification.objects.values().get(pk=self.other.pk)
        client = self.client_for("editor")
        payload = {
            **self.payload, "id": self.other.pk, "star_count": 100,
            "is_starred": False, "starred_by_names": "forged",
            "starred_by": [self.users["owner"].pk],
        }
        for method in ("put", "patch"):
            with self.subTest(method=method):
                response = getattr(client, method)(self.url, payload, format="json")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data["id"], self.target.pk)
                self.assertEqual(response.data["star_count"], 2)
                self.assertTrue(response.data["is_starred"])
                self.assertEqual(set(self.target.starred_by.values_list("pk", flat=True)), {
                    self.users["member"].pk, self.users["editor"].pk,
                })
                self.assertEqual(Certification.objects.values().get(pk=self.other.pk), other_before)
                self.assertEqual(Certification.objects.count(), 2)

    def test_session_updates_require_csrf_for_owner_and_editor(self):
        for role in ("owner", "editor"):
            client = self.client_for(role, enforce_csrf=True)
            token = self.csrf_token(client)
            for method in ("put", "patch"):
                with self.subTest(role=role, method=method):
                    before = self.saved_state()
                    denied = getattr(client, method)(self.url, self.payload, format="json")
                    self.assertEqual(denied.status_code, 403)
                    self.assertIn("CSRF", str(denied.data["detail"]))
                    self.assertEqual(self.saved_state(), before)
                    allowed = getattr(client, method)(
                        self.url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
                    )
                    self.assertEqual(allowed.status_code, 200)

    def test_session_delete_requires_csrf_even_for_owner(self):
        client = self.client_for("owner", enforce_csrf=True)
        token = self.csrf_token(client)
        before = self.saved_state()
        denied = client.delete(self.url)
        self.assertEqual(denied.status_code, 403)
        self.assertIn("CSRF", str(denied.data["detail"]))
        self.assertEqual(self.saved_state(), before)
        allowed = client.delete(self.url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(allowed.status_code, 204)
        self.assertFalse(Certification.objects.filter(pk=self.target.pk).exists())

    def test_malformed_json_updates_return_400_without_mutation(self):
        before = self.saved_state()
        client = self.client_for("owner")
        for method in ("put", "patch"):
            with self.subTest(method=method):
                response = getattr(client, method)(
                    self.url, '{"title":', content_type="application/json",
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(self.saved_state(), before)

    def test_post_is_not_supported_on_detail_endpoint(self):
        before = self.saved_state()
        response = self.client_for("owner").post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.saved_state(), before)


class CertificationStarAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        Certification.objects.all().delete()
        cls.users = {
            "member": User.objects.create_user(
                username="star_member", email="private-star@example.com",
            ),
            "editor": User.objects.create_user(username="star_editor"),
            "owner": User.objects.create_user(username="star_owner", is_superuser=True),
        }
        cls.users["editor"].groups.add(Group.objects.get_or_create(name="Editor")[0])
        cls.other_user = User.objects.create_user(username="existing_star")
        cls.target = Certification.objects.create(
            title="Star target", description="Target description", year=2026,
        )
        cls.target.starred_by.add(cls.other_user)
        cls.other = Certification.objects.create(
            title="Unrelated", description="Other description", year=2025,
        )
        cls.url = reverse("api:certification-star", args=[cls.target.pk])

    def client_for(self, role, enforce_csrf=False):
        client = APIClient(enforce_csrf_checks=enforce_csrf)
        client.force_login(self.users[role])
        return client

    def test_anonymous_requests_are_denied_without_changing_stars(self):
        for method in ("get", "post"):
            with self.subTest(method=method):
                self.assertEqual(getattr(self.client, method)(self.url).status_code, 403)
        self.assertEqual(list(self.target.starred_by.all()), [self.other_user])

    def test_members_editors_and_owner_can_toggle_only_their_own_star(self):
        for role in self.users:
            client = self.client_for(role)
            for expected_flag, expected_count in ((True, 2), (False, 1)):
                with self.subTest(role=role, starred=expected_flag):
                    response = client.post(self.url)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.data["id"], self.target.pk)
                    self.assertEqual(response.data["is_starred"], expected_flag)
                    self.assertEqual(response.data["star_count"], expected_count)
                    self.assertEqual(
                        self.target.starred_by.filter(pk=self.users[role].pk).exists(),
                        expected_flag,
                    )
                    self.assertTrue(self.target.starred_by.filter(pk=self.other_user.pk).exists())
        self.assertFalse(self.other.starred_by.exists())

    def test_payload_cannot_choose_a_different_user_or_forge_star_fields(self):
        response = self.client_for("member").post(self.url, {
            "user": self.users["owner"].pk,
            "user_id": self.users["owner"].pk,
            "id": self.other.pk,
            "starred_by": [self.users["owner"].pk],
            "star_count": 999, "is_starred": False, "starred_by_names": "forged",
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.target.pk)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 2)
        self.assertEqual(set(self.target.starred_by.values_list("pk", flat=True)), {
            self.other_user.pk, self.users["member"].pk,
        })
        self.assertFalse(self.other.starred_by.exists())

    def test_authenticated_nonpost_methods_do_not_change_data(self):
        client = self.client_for("member")
        for method in ("get", "head", "put", "patch", "delete"):
            with self.subTest(method=method):
                self.assertEqual(getattr(client, method)(self.url).status_code, 405)
                self.assertEqual(list(self.target.starred_by.all()), [self.other_user])
        self.assertEqual(client.options(self.url).status_code, 200)
        self.assertEqual(list(self.target.starred_by.all()), [self.other_user])

    def test_missing_certification_returns_404_without_creating_relations(self):
        url = reverse("api:certification-star", args=[self.other.pk + 1000])
        response = self.client_for("member").post(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Certification.starred_by.through.objects.count(), 1)

    def test_session_star_requires_matching_csrf_cookie_and_header(self):
        client = self.client_for("member", enforce_csrf=True)
        client.get(reverse("rest_framework:login"))
        token = client.cookies[settings.CSRF_COOKIE_NAME].value
        for headers in ({}, {"HTTP_X_CSRFTOKEN": "invalid-token"}):
            with self.subTest(headers=headers):
                response = client.post(self.url, **headers)
                self.assertEqual(response.status_code, 403)
                self.assertIn("CSRF", str(response.data["detail"]))
                self.assertEqual(list(self.target.starred_by.all()), [self.other_user])
        allowed = client.post(self.url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(allowed.status_code, 200)
        self.assertTrue(allowed.data["is_starred"])

    def test_response_contains_public_certification_fields_only(self):
        response = self.client_for("member").post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), {
            "id", "title", "description", "year", "is_highlight",
            "star_count", "is_starred", "starred_by_names",
        })
        self.assertEqual(set(response.data["starred_by_names"].split(", ")), {
            "existing_star", "star_member",
        })
        self.assertNotContains(response, "private-star@example.com")

    def test_repeated_toggles_never_duplicate_a_users_relation(self):
        client = self.client_for("member")
        for expected_flag in (True, False, True, False):
            response = client.post(self.url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["is_starred"], expected_flag)
            self.assertEqual(
                self.target.starred_by.filter(pk=self.users["member"].pk).count(),
                int(expected_flag),
            )
            self.assertEqual(self.target.starred_by.count(), 1 + int(expected_flag))

    def test_list_and_detail_reflect_the_new_star_for_the_current_account(self):
        client = self.client_for("member")
        self.assertEqual(client.post(self.url).status_code, 200)
        detail = client.get(reverse("api:certification-detail", args=[self.target.pk]))
        listing = client.get(reverse("api:certification-list"), {"starred": "1"})
        self.assertTrue(detail.data["is_starred"])
        self.assertEqual(detail.data["star_count"], 2)
        self.assertEqual([row["id"] for row in listing.data], [self.target.pk])
        other_viewer = self.client_for("owner").get(
            reverse("api:certification-detail", args=[self.target.pk]),
        )
        self.assertFalse(other_viewer.data["is_starred"])
        self.assertEqual(other_viewer.data["star_count"], 2)
