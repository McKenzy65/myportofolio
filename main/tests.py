from django.test import TestCase, Client
from main.models import Experience

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