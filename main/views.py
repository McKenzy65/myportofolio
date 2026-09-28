from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from main.models import Experience, Certification
from main.forms import CertificationForm
from django.http import HttpResponse
from django.core import serializers
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render
import datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied        

PORTFOLIO_OWNER = 'Umar Faiz Rahman'

@login_required(login_url="/login/")
def toggle_star(request, certification_id):
    """Pengguna login memberi/membatalkan star (maksimal satu per pengguna)."""
    certification = get_object_or_404(Certification, pk=certification_id)
    if request.method == "POST":
        if request.user in certification.starred_by.all():
            certification.starred_by.remove(request.user)
        else:
            certification.starred_by.add(request.user)
    return redirect("main:show_certifications")


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": PORTFOLIO_OWNER,
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": PORTFOLIO_OWNER,
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": PORTFOLIO_OWNER,
        "npm": "2506616711",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang sedang belajar "
            "pada pengembangan perangkat lunak dan pendidikan."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)

@login_required(login_url="/login/")
def create_certification(request):
    """Hanya pemilik portofolio (superuser) yang boleh menambah data."""
    if not request.user.is_superuser:
        raise PermissionDenied
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

@login_required(login_url="/login/")
def edit_certification(request, certification_id):
    """Superuser atau anggota grup Editor boleh mengubah data yang sudah ada."""
    is_editor = request.user.groups.filter(name="Editor").exists()
    if not (request.user.is_superuser or is_editor):
        raise PermissionDenied
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

@login_required(login_url="/login/")
def delete_certification(request, certification_id):
    """Hanya pemilik portofolio (superuser) yang boleh menghapus data."""
    if not request.user.is_superuser:
        raise PermissionDenied
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

    return HttpResponse(
        serializers.serialize("json", certifications, use_natural_foreign_keys=True),
        content_type="application/json",
    )

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

    is_editor = (
        request.user.is_authenticated
        and request.user.groups.filter(name="Editor").exists()
    )

    context = {
        "name": PORTFOLIO_OWNER,
        "certification_list": certifications,
        "title_query": title_query,
        "is_editor": is_editor,
    }
    return render(request, "certifications.html", context)