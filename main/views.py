from django.shortcuts import render
from main.models import Experience

def show_main(request):
    experience_list = Experience.objects.all()

    context = {
        'name': 'Umar Faiz Rahman',
        'npm': '2506616711',
        'study_program': 'S1 Sistem Informasi',
        'bio': 'Mahasiswa Sistem Informasi Universitas Indonesia',
        'experience_list': experience_list,
    }
    return render(request, "index.html", context)