from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPortfolioOwnerOrReadOnly(BasePermission):
    """Public reading; only the portfolio superuser may write."""

    message = "Hanya pemilik portofolio yang boleh mengubah data."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_superuser


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """Editors may update existing data; create/delete remain owner-only."""

    message = (
        "Hanya pemilik yang boleh menambah atau menghapus data. "
        "Pemilik dan Editor boleh mengubah data."
    )

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return (
            request.method in ("PUT", "PATCH")
            and request.user.groups.filter(name="Editor").exists()
        )
