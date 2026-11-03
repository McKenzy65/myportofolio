from django.db.models import Count
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes,
)
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from main.models import Certification
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly
from main.serializers import CertificationSerializer


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
