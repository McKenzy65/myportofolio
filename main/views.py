from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from main.models import Experience, Certification
from main.forms import CertificationForm
from django.http import HttpResponse
from django.core import serializers

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

def get_certifications_json(request):
    title_query = request.GET.get("title", "").strip()
    certifications = Certification.objects.all()

    if title_query:
        certifications = certifications.filter(title__icontains=title_query)

    certifications_json = serializers.serialize("json", certifications)
    return HttpResponse(certifications_json, content_type="application/json")

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