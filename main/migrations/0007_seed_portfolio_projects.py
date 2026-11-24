from django.db import migrations


# Existing public projects from the portfolio homepage at the time of migration.
PROJECTS = [
    {
        "id": "f70adb9c-6609-544d-8701-56be3e890c7a",
        "title": "Dione AI, AI-Powered Learning System",
        "description": (
            "Berperan sebagai project lead untuk platform edukasi berbasis AI dan IoT "
            "menggunakan Arduino, mencakup absensi wajah, kontrol suara, hingga ringkasan "
            "materi otomatis. Meraih Juara 2 Samsung Solve for Tomorrow Indonesia 2024."
        ),
        "tech_stack": "C++, AI, IoT, Arduino",
        "project_url": "https://news.samsung.com/id/inovasi-ai-terbaik-di-samsung-solve-for-tomorrow-buatan-anak-bangsa-untuk-indonesia",
        "project_image_url": "https://umar-faiz-myportofolio.pws.cs.ui.ac.id/static/img/dione-samsung.jpg",
    },
    {
        "id": "f6a0215a-eaac-5035-b065-0699e23da82e",
        "title": "Dione AI, Pesta Sains Nasional IPB",
        "description": (
            "Membawa Dione AI sebagai finalis STEM Young Researcher Award di Pesta Sains "
            "Nasional, IPB University (2024). Salah satu fitur utamanya adalah absensi "
            "berbasis pengenalan wajah."
        ),
        "tech_stack": "AI, IoT, Arduino",
        "project_url": "https://umar-faiz-myportofolio.pws.cs.ui.ac.id/certifications/",
        "project_image_url": "https://umar-faiz-myportofolio.pws.cs.ui.ac.id/static/img/dione-psn.webp",
    },
    {
        "id": "59c7c2e5-9a17-5db1-ac45-464a4fbadfd4",
        "title": "SBF, proyek back-end BEM Fasilkom UI",
        "description": (
            "Turut mengerjakan back-end untuk salah satu program kerja BEM Fasilkom UI, "
            "mulai dari logika data hingga endpoint aplikasi."
        ),
        "tech_stack": "Back-End, Web",
        "project_url": "https://github.com/",
        "project_image_url": "",
    },
    {
        "id": "ac3b772c-f43d-5fb8-ae67-776268887748",
        "title": "Game project, Infinite Learning",
        "description": (
            "Turut mengembangkan game dalam program Infinite Learning, menangani gameplay "
            "programming dengan C# dan berkolaborasi dengan tim melalui Git."
        ),
        "tech_stack": "C#, Game Dev, Git",
        "project_url": "https://github.com/",
        "project_image_url": "https://umar-faiz-myportofolio.pws.cs.ui.ac.id/static/img/infinite-learning.webp",
    },
]


def seed_projects(apps, schema_editor):
    projects = apps.get_model("main", "Project").objects.using(schema_editor.connection.alias)
    projects.bulk_create(projects.model(**fields) for fields in PROJECTS)


def remove_seeded_projects(apps, schema_editor):
    projects = apps.get_model("main", "Project").objects.using(schema_editor.connection.alias)
    for fields in PROJECTS:
        projects.filter(**fields).delete()


class Migration(migrations.Migration):
    dependencies = [("main", "0006_project")]
    operations = [migrations.RunPython(seed_projects, remove_seeded_projects)]
