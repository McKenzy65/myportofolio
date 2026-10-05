from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from main.models import Experience, Certification
from main.forms import CertificationForm, PortfolioAuthenticationForm, PortfolioUserCreationForm
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.core import serializers
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
import datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied        
from django.contrib.auth.views import redirect_to_login
from django.db.models import Count

PORTFOLIO_OWNER = 'Umar Faiz Rahman'

@require_POST
def toggle_star(request, certification_id):
    """Pengguna login memberi/membatalkan star (maksimal satu per pengguna)."""
    wants_json = "application/json" in request.headers.get("Accept", "")
    if not request.user.is_authenticated:
        if wants_json:
            return JsonResponse({"message": "Silakan login untuk memberi star."}, status=403)
        return redirect_to_login(request.get_full_path(), login_url="/login/")

    certification = get_object_or_404(Certification, pk=certification_id)
    is_starred = certification.starred_by.filter(pk=request.user.pk).exists()
    if is_starred:
        certification.starred_by.remove(request.user)
    else:
        certification.starred_by.add(request.user)

    if wants_json:
        return JsonResponse({
            "message": "Star dibatalkan." if is_starred else "Sertifikasi ditambahkan ke favorit.",
            "is_starred": not is_starred,
            "star_count": certification.starred_by.count(),
        })
    return redirect("main:show_certifications")


def register(request):
    form = PortfolioUserCreationForm(request.POST or None)

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
    form = PortfolioAuthenticationForm(request, data=request.POST or None)

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
            "Computer Science student @Universitas Indonesia, exploring software, "
            "technology, and whatever seems worth building."
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
    """Data sertifikasi dalam JSON, termasuk info star untuk pengguna saat ini.

    Filter judul, tahun, unggulan, dan favorit dapat digabungkan. Pengurutan
    memakai pilihan tetap agar query pengguna tidak menjadi nama field ORM.
    """
    title_query = request.GET.get("title", "").strip()
    certifications = Certification.objects.prefetch_related("starred_by").all()

    if title_query:
        certifications = certifications.filter(title__icontains=title_query)

    year = request.GET.get("year", "").strip()
    if year:
        try:
            year_number = int(year)
            if not 0 <= year_number <= 2147483647:
                raise ValueError
        except ValueError:
            return JsonResponse({"message": "Filter tahun harus berupa angka tahun yang valid."}, status=400)
        certifications = certifications.filter(year=year_number)

    if request.GET.get("highlight") == "1":
        certifications = certifications.filter(is_highlight=True)
    if request.GET.get("starred") == "1":
        if not request.user.is_authenticated:
            return JsonResponse({"message": "Silakan login untuk melihat favorit."}, status=403)
        certifications = certifications.filter(starred_by=request.user)

    sort = request.GET.get("sort", "newest")
    orderings = {"newest": ("-year", "-pk"), "oldest": ("year", "pk"), "title": ("title", "pk")}
    if sort == "popular":
        certifications = certifications.annotate(total_stars=Count("starred_by", distinct=True)).order_by("-total_stars", "-year", "-pk")
    else:
        certifications = certifications.order_by(*orderings.get(sort, orderings["newest"]))

    data = []
    for cert in certifications:
        starred_users = list(cert.starred_by.all())
        is_starred = request.user.is_authenticated and request.user in starred_users
        data.append({
            "model": "main.certification",
            "pk": cert.pk,
            "fields": {
                "title": cert.title,
                "description": cert.description,
                "year": cert.year,
                "is_highlight": cert.is_highlight,
                "star_count": len(starred_users),
                "is_starred": is_starred,
                "starred_by_names": ", ".join(u.username for u in starred_users),
            },
        })
    return JsonResponse(data, safe=False)

def get_experiences_json(request):
    """Data pengalaman dalam JSON. Mendukung filter kategori lewat ?category=."""
    category_query = request.GET.get("category", "").strip()
    experiences = Experience.objects.all()

    if category_query:
        experiences = experiences.filter(category=category_query)

    return json_response(experiences)

def show_certifications(request):
    """Halaman kerangka sertifikasi; datanya diambil browser lewat AJAX."""
    is_editor = (
        request.user.is_authenticated
        and request.user.groups.filter(name="Editor").exists()
    )

    context = {
        "name": PORTFOLIO_OWNER,
        "title_query": request.GET.get("title", "").strip(),
        "is_editor": is_editor,
        "form": CertificationForm(),
        "certification_years": Certification.objects.order_by("-year").values_list("year", flat=True).distinct(),
    }
    return render(request, "certifications.html", context)


@require_POST
def create_certification_ajax(request):
    """Tambah sertifikasi lewat AJAX. Hanya superuser; balasan selalu JSON."""
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan sertifikasi."},
            status=403,
        )

    form = CertificationForm(request.POST)
    if form.is_valid():
        certification = form.save()
        return JsonResponse(
            {"message": "Sertifikasi berhasil ditambahkan.", "pk": certification.pk},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
