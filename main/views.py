from django.shortcuts import render
from main.models import Experience, Certification

PORTFOLIO_OWNER = 'Umar Faiz Rahman'

def show_main(request):
    experience_list = Experience.objects.all()

    context = {
        'name': PORTFOLIO_OWNER,
        'npm': '2506616711',
        'study_program': 'S1 Sistem Informasi',
        'bio': 'Mahasiswa Sistem Informasi Universitas Indonesia',
        'experience_list': experience_list,
    }
    return render(request, "index.html", context)

def show_certifications(request):
    certification_list = Certification.objects.all().order_by('-year')

    context = {
        'name': PORTFOLIO_OWNER,
        'certification_list': certification_list,
    }
    return render(request, "certifications.html", context)