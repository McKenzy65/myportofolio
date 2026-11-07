from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes,
)
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Certification, Experience
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly
from main.serializers import CertificationSerializer, ExperienceSerializer


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def certification_list(request):
    if request.method in ("GET", "HEAD"):
        certifications = Certification.objects.prefetch_related("starred_by")
        sort = request.query_params.get("sort", "newest")
        if sort == "popular":
            # Count all stars before limiting the list to this user's favorites.
            certifications = certifications.annotate(
                total_stars=Count("starred_by", distinct=True),
            )

        title = request.query_params.get("title", "").strip()
        if title:
            certifications = certifications.filter(title__icontains=title)

        year = request.query_params.get("year", "").strip()
        if year:
            try:
                year_number = int(year)
                if not 0 <= year_number <= 2147483647:
                    raise ValueError
            except ValueError:
                raise ValidationError({
                    "year": ["Filter tahun harus berupa angka tahun yang valid."],
                })
            certifications = certifications.filter(year=year_number)

        if request.query_params.get("highlight") == "1":
            certifications = certifications.filter(is_highlight=True)
        if request.query_params.get("starred") == "1":
            if not request.user.is_authenticated:
                raise PermissionDenied("Silakan login untuk melihat favorit.")
            certifications = certifications.filter(starred_by=request.user)

        orderings = {
            "newest": ("-year", "-pk"),
            "oldest": ("year", "pk"),
            "title": ("title", "pk"),
            "popular": ("-total_stars", "-year", "-pk"),
        }
        certifications = certifications.order_by(
            *orderings.get(sort, orderings["newest"]),
        )
        serializer = CertificationSerializer(
            certifications, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = CertificationSerializer(
        data=request.data, context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def certification_detail(request, certification_id):
    certification = get_object_or_404(
        Certification.objects.prefetch_related("starred_by"), pk=certification_id,
    )

    if request.method in ("GET", "HEAD"):
        serializer = CertificationSerializer(
            certification, context={"request": request},
        )
        return Response(serializer.data)

    if request.method == "DELETE":
        certification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = CertificationSerializer(
        certification, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def certification_star(request, certification_id):
    certification = get_object_or_404(Certification, pk=certification_id)
    if certification.starred_by.filter(pk=request.user.pk).exists():
        certification.starred_by.remove(request.user)
    else:
        certification.starred_by.add(request.user)
    serializer = CertificationSerializer(
        certification, context={"request": request},
    )
    return Response(serializer.data)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_list(request):
    if request.method in ("GET", "HEAD"):
        experiences = Experience.objects.prefetch_related("starred_by")
        title = request.query_params.get("title", "").strip()
        category = request.query_params.get("category", "").strip()
        if title:
            experiences = experiences.filter(title__icontains=title)
        if category:
            if category not in dict(Experience.EXPERIENCE_CHOICES):
                raise ValidationError({"category": ["Kategori pengalaman tidak valid."]})
            experiences = experiences.filter(category=category)
        experiences = experiences.order_by("-started_at", "pk")
        serializer = ExperienceSerializer(
            experiences, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = ExperienceSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_detail(request, experience_id):
    experience = get_object_or_404(
        Experience.objects.prefetch_related("starred_by"), pk=experience_id,
    )
    if request.method in ("GET", "HEAD"):
        serializer = ExperienceSerializer(experience, context={"request": request})
        return Response(serializer.data)
    if request.method == "DELETE":
        experience.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ExperienceSerializer(
        experience, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def experience_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if experience.starred_by.filter(pk=request.user.pk).exists():
        experience.starred_by.remove(request.user)
    else:
        experience.starred_by.add(request.user)
    serializer = ExperienceSerializer(experience, context={"request": request})
    return Response(serializer.data)
