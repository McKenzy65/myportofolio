from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from main.models import Experience, Certification
from main.forms import CertificationForm
from django.http import HttpResponse
from django.core import serializers
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render

PORTFOLIO_OWNER = 'Umar Faiz Rahman'

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Burhan",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("main:show_main")

    context = {
        "name": "Burhan",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    return redirect("main:show_main")


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

def create_certification(request):
    form = CertificationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sertifikasi baru berhasil ditambahkan!")
        return redirect("main:show_certifications")

    context = {
        "name": PORTFOLIO_OWNER,
        "form": form,
        "page_title": "Tambah Sertifikasi Baru",
    }
    return render(request, "certification_form.html", context)

def edit_certification(request, certification_id):
    certification = get_object_or_404(Certification, pk=certification_id)
    form = CertificationForm(request.POST or None, instance=certification)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sertifikasi berhasil diperbarui!")
        return redirect("main:show_certifications")

    context = {
        "name": PORTFOLIO_OWNER,
        "form": form,
        "page_title": "Edit Sertifikasi",
    }
    return render(request, "certification_form.html", context)

def delete_certification(request, certification_id):
    certification = get_object_or_404(Certification, pk=certification_id)

    if request.method == "POST":
        certification.delete()
        messages.success(request, "Sertifikasi berhasil dihapus")
        return redirect("main:show_certifications")

    return redirect("main:show_certifications")

def json_response(queryset):
    """Serialisasi queryset model Django ke response JSON."""
    return HttpResponse(
        serializers.serialize("json", queryset),
        content_type="application/json",
    )

def get_certifications_json(request):
    """Data sertifikasi dalam JSON. Mendukung filter judul lewat ?title=."""
    title_query = request.GET.get("title", "").strip()
    certifications = Certification.objects.all()

    if title_query:
        certifications = certifications.filter(title__icontains=title_query)

    return json_response(certifications)

def get_experiences_json(request):
    """Data pengalaman dalam JSON. Mendukung filter kategori lewat ?category=."""
    category_query = request.GET.get("category", "").strip()
    experiences = Experience.objects.all()

    if category_query:
        experiences = experiences.filter(category=category_query)

    return json_response(experiences)

def show_certifications(request):
    json_response = get_certifications_json(request)
    certifications = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    certifications = [cert.object for cert in certifications]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": PORTFOLIO_OWNER,
        "certification_list": certifications,
        "title_query": title_query,
    }
    return render(request, "certifications.html", context)