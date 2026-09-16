from django.shortcuts import render, redirect
from django.contrib import messages
from main.models import Experience, Certification
from main.forms import CertificationForm


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
    certification_list = Certification.objects.all()

    context = {
        'name': PORTFOLIO_OWNER,
        'certification_list': certification_list,
    }
    return render(request, "certifications.html", context)

def create_certification(request):
    form = CertificationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sertifikasi baru berhasil ditambahkan!")
        return redirect("main:show_certifications")

    context = {
        "name": PORTFOLIO_OWNER,
        "form": form,
    }
    return render(request, "certification_form.html", context)