from django.test import TestCase, Client
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