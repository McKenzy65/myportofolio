from django.db import migrations

CERTIFICATIONS = [
    {
        'title': 'Juara 2 Samsung Solve for Tomorrow Indonesia',
        'description': 'Samsung Electronics - lewat inovasi Dione AI. Prototipe meraih skor usability (SUS) 97%.',
        'year': 2024,
        'is_highlight': True,
    },
    {
        'title': 'Finalist STEM Young Researcher Award',
        'description': 'Pesta Sains Nasional, IPB University.',
        'year': 2024,
        'is_highlight': False,
    },
    {
        'title': 'Google Project Management (Professional Certificate)',
        'description': 'Google - spesialisasi lengkap via Coursera.',
        'year': 2026,
        'is_highlight': False,
    },
    {
        'title': 'IELTS',
        'description': 'British Council.',
        'year': 2024,
        'is_highlight': False,
    },
    {
        'title': 'UKBI - Predikat Unggul',
        'description': 'Kemendikbud, skor 632.',
        'year': 2026,
        'is_highlight': False,
    },
    {
        'title': 'Design Thinking',
        'description': 'Samsung Indonesia.',
        'year': 2024,
        'is_highlight': False,
    },
]


def populate_certifications(apps, schema_editor):
    Certification = apps.get_model('main', 'Certification')
    for data in CERTIFICATIONS:
        Certification.objects.create(**data)


def remove_certifications(apps, schema_editor):
    Certification = apps.get_model('main', 'Certification')
    Certification.objects.filter(title__in=[c['title'] for c in CERTIFICATIONS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_certification'),
    ]

    operations = [
        migrations.RunPython(populate_certifications, remove_certifications),
    ]
