import json

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from main.models import Experience, Certification

class MainTest(TestCase):
    def test_main_url_is_exist(self):
        response = Client().get('/')
        self.assertEqual(response.status_code, 200)

    def test_main_using_main_template(self):
        response = Client().get('/')
        self.assertTemplateUsed(response, 'index.html')

    def test_experience_creation(self):
        exp = Experience.objects.create(
            title="Finance",
            description="Mengelola operasional keuangan.",
            category="volunteer"
        )
        self.assertEqual(exp.title, "Finance")
        self.assertEqual(exp.category, "volunteer")
        self.assertTrue(exp.is_ongoing)

class CertificationTest(TestCase):
    def test_certifications_url_is_exist(self):
        response = Client().get('/certifications/')
        self.assertEqual(response.status_code, 200)

    def test_certifications_using_correct_template(self):
        response = Client().get('/certifications/')
        self.assertTemplateUsed(response, 'certifications.html')

    def test_certification_creation(self):
        cert = Certification.objects.create(
            title="UKBI - Predikat Unggul",
            description="Kemendikbud, skor 632.",
            year=2026,
        )
        self.assertEqual(cert.title, "UKBI - Predikat Unggul")
        self.assertEqual(cert.year, 2026)
        self.assertFalse(cert.is_highlight)

    def test_certifications_page_displays_data_when_available(self):
        Certification.objects.create(
            title="IELTS",
            description="British Council.",
            year=2024,
        )
        response = Client().get('/certifications/')
        self.assertContains(response, "IELTS")

    def test_certifications_page_displays_empty_state(self):
        Certification.objects.all().delete()
        response = Client().get('/certifications/')
        self.assertContains(response, "Belum ada data sertifikasi di database.")

class CertificationCrudTest(TestCase):
    """Create, update, dan delete sertifikasi lewat form."""

    def setUp(self):
        # migrasi data mengisi tabel dengan data awal, jadi dikosongkan dulu
        Certification.objects.all().delete()
        self.superuser = User.objects.create_superuser(
            username="admin_test", password="testpass123"
        )
        self.client.force_login(self.superuser)
        self.cert = Certification.objects.create(
            title="IELTS",
            description="British Council.",
            year=2024,
        )
        self.valid_data = {
            "title": "Google Project Management",
            "description": "Spesialisasi via Coursera.",
            "year": 2026,
            "is_highlight": "on",
        }

    def test_create_page_uses_form_template(self):
        response = self.client.get(reverse("main:create_certification"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "certification_form.html")
        self.assertContains(response, "Tambah Sertifikasi Baru")

    def test_create_with_valid_data_saves_and_redirects(self):
        response = self.client.post(reverse("main:create_certification"), self.valid_data)
        self.assertRedirects(response, reverse("main:show_certifications"))
        self.assertEqual(Certification.objects.count(), 2)
        created = Certification.objects.get(title="Google Project Management")
        self.assertEqual(created.year, 2026)
        self.assertTrue(created.is_highlight)

    def test_create_with_invalid_data_does_not_save(self):
        data = {**self.valid_data, "year": "bukan-angka"}
        response = self.client.post(reverse("main:create_certification"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("year", response.context["form"].errors)
        self.assertEqual(Certification.objects.count(), 1)

    def test_create_shows_flash_message_after_redirect(self):
        response = self.client.post(
            reverse("main:create_certification"), self.valid_data, follow=True
        )
        self.assertContains(response, "berhasil ditambahkan")

    def test_edit_page_is_prefilled_with_existing_data(self):
        response = self.client.get(reverse("main:edit_certification", args=[self.cert.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Sertifikasi")
        self.assertContains(response, "IELTS")

    def test_edit_updates_existing_certification(self):
        response = self.client.post(
            reverse("main:edit_certification", args=[self.cert.pk]),
            {"title": "IELTS Academic", "description": "British Council.", "year": 2025},
        )
        self.assertRedirects(response, reverse("main:show_certifications"))
        self.cert.refresh_from_db()
        self.assertEqual(self.cert.title, "IELTS Academic")
        self.assertEqual(self.cert.year, 2025)
        self.assertEqual(Certification.objects.count(), 1)

    def test_edit_missing_certification_returns_404(self):
        response = self.client.get(reverse("main:edit_certification", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_with_post_removes_certification(self):
        response = self.client.post(reverse("main:delete_certification", args=[self.cert.pk]))
        self.assertRedirects(response, reverse("main:show_certifications"))
        self.assertEqual(Certification.objects.count(), 0)

    def test_delete_with_get_does_not_remove_certification(self):
        response = self.client.get(reverse("main:delete_certification", args=[self.cert.pk]))
        self.assertRedirects(response, reverse("main:show_certifications"))
        self.assertEqual(Certification.objects.count(), 1)

    def test_delete_missing_certification_returns_404(self):
        response = self.client.post(reverse("main:delete_certification", args=[9999]))
        self.assertEqual(response.status_code, 404)


class JsonDeliveryTest(TestCase):
    """Endpoint JSON dan tampilan halaman yang memakai hasil deserialisasi."""

    def setUp(self):
        Certification.objects.all().delete()
        Experience.objects.all().delete()
        Certification.objects.create(title="IELTS", description="British Council.", year=2024)
        Certification.objects.create(title="Google Project Management", description="Coursera.", year=2026)

    def test_certifications_json_returns_serialized_data(self):
        response = self.client.get(reverse("main:get_certifications_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["model"], "main.certification")
        self.assertIn("title", data[0]["fields"])

    def test_certifications_json_filters_by_title_case_insensitive(self):
        response = self.client.get(reverse("main:get_certifications_json"), {"title": "google"})
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["fields"]["title"], "Google Project Management")

    def test_certifications_page_search_uses_title_query(self):
        response = self.client.get(reverse("main:show_certifications"), {"title": "ielts"})
        self.assertContains(response, "IELTS")
        self.assertNotContains(response, "Google Project Management")

    def test_experiences_json_returns_data_and_filters_by_category(self):
        Experience.objects.create(title="Riset AI", description="Riset.", category="research")
        Experience.objects.create(title="Panitia", description="Kepanitiaan.", category="volunteer")

        all_response = self.client.get(reverse("main:get_experiences_json"))
        self.assertEqual(all_response["Content-Type"], "application/json")
        self.assertEqual(len(json.loads(all_response.content)), 2)

        filtered = self.client.get(reverse("main:get_experiences_json"), {"category": "research"})
        data = json.loads(filtered.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["fields"]["title"], "Riset AI")


class RoleAuthorizationTest(TestCase):
    """Hak akses 4 peran: pengunjung, user biasa, editor, superuser."""

    def setUp(self):
        Certification.objects.all().delete()
        self.cert = Certification.objects.create(
            title="IELTS", description="British Council.", year=2024
        )

        from django.contrib.auth.models import Group

        self.editor_group, _ = Group.objects.get_or_create(name="Editor")

        self.regular_user = User.objects.create_user(
            username="regular_test", password="testpass123"
        )
        self.editor_user = User.objects.create_user(
            username="editor_test", password="testpass123"
        )
        self.editor_user.groups.add(self.editor_group)
        self.superuser = User.objects.create_superuser(
            username="owner_test", password="testpass123"
        )

    def test_anonymous_redirected_to_login_on_create(self):
        response = self.client.get(reverse("main:create_certification"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_regular_user_forbidden_from_create(self):
        self.client.login(username="regular_test", password="testpass123")
        response = self.client.get(reverse("main:create_certification"))
        self.assertEqual(response.status_code, 403)

    def test_regular_user_forbidden_from_edit(self):
        self.client.login(username="regular_test", password="testpass123")
        response = self.client.get(
            reverse("main:edit_certification", args=[self.cert.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_regular_user_forbidden_from_delete(self):
        self.client.login(username="regular_test", password="testpass123")
        response = self.client.post(
            reverse("main:delete_certification", args=[self.cert.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_regular_user_can_toggle_star(self):
        self.client.login(username="regular_test", password="testpass123")
        response = self.client.post(
            reverse("main:toggle_star", args=[self.cert.pk])
        )
        self.assertRedirects(response, reverse("main:show_certifications"))
        self.assertIn(self.regular_user, self.cert.starred_by.all())

        # toggle lagi: star dibatalkan, tidak boleh dobel
        self.client.post(reverse("main:toggle_star", args=[self.cert.pk]))
        self.assertNotIn(self.regular_user, self.cert.starred_by.all())

    def test_editor_can_edit_but_not_create_or_delete(self):
        self.client.login(username="editor_test", password="testpass123")

        edit_response = self.client.post(
            reverse("main:edit_certification", args=[self.cert.pk]),
            {"title": "IELTS Academic", "description": "British Council.", "year": 2025},
        )
        self.assertRedirects(edit_response, reverse("main:show_certifications"))
        self.cert.refresh_from_db()
        self.assertEqual(self.cert.title, "IELTS Academic")

        create_response = self.client.get(reverse("main:create_certification"))
        self.assertEqual(create_response.status_code, 403)

        delete_response = self.client.post(
            reverse("main:delete_certification", args=[self.cert.pk])
        )
        self.assertEqual(delete_response.status_code, 403)

    def test_superuser_can_create_edit_and_delete(self):
        self.client.login(username="owner_test", password="testpass123")

        create_response = self.client.post(
            reverse("main:create_certification"),
            {"title": "New Cert", "description": "Desc.", "year": 2026},
        )
        self.assertRedirects(create_response, reverse("main:show_certifications"))

        delete_response = self.client.post(
            reverse("main:delete_certification", args=[self.cert.pk])
        )
        self.assertRedirects(delete_response, reverse("main:show_certifications"))
        self.assertFalse(Certification.objects.filter(pk=self.cert.pk).exists())

    def test_json_endpoint_does_not_leak_user_id(self):
        self.cert.starred_by.add(self.regular_user)
        response = self.client.get(reverse("main:get_certifications_json"))
        data = json.loads(response.content)
        starred = next(c["fields"]["starred_by"] for c in data if c["pk"] == self.cert.pk)
        self.assertEqual(starred, [["regular_test"]])
