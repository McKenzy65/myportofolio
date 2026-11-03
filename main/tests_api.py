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
