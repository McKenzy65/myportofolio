from django.contrib.auth.models import Group, User
from django.middleware.csrf import get_token
from django.test import override_settings
from django.urls import path
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import APIView

from main.permissions import (
    IsPortfolioOwnerOrEditorOrReadOnly,
    IsPortfolioOwnerOrReadOnly,
)


class PermissionProbeView(APIView):
    """Test-only endpoint: exercise DRF authentication without changing data."""

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsPortfolioOwnerOrReadOnly]

    def get(self, request):
        return Response({
            "username": request.user.get_username(),
            "csrf_token": get_token(request),
        })

    post = get
    put = get
    patch = get
    delete = get


# These routes are used only by this test module, not by the application URLs.
urlpatterns = [
    path("owner/", PermissionProbeView.as_view()),
    path("editor/", PermissionProbeView.as_view(
        permission_classes=[IsPortfolioOwnerOrEditorOrReadOnly],
    )),
    path("authenticated/", PermissionProbeView.as_view(
        permission_classes=[IsAuthenticated],
    )),
]


@override_settings(ROOT_URLCONF=__name__)
class PortfolioPermissionTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = {
            "member": User.objects.create_user(username="member"),
            "staff": User.objects.create_user(username="staff", is_staff=True),
            "editor": User.objects.create_user(username="editor"),
            "owner": User.objects.create_user(
                username="owner", is_superuser=True, is_staff=True,
            ),
        }
        cls.users["editor"].groups.add(Group.objects.create(name="Editor"))

    def client_for(self, role, enforce_csrf=False):
        client = APIClient(enforce_csrf_checks=enforce_csrf)
        if role is not None:
            client.force_login(self.users[role])
        return client

    def test_read_methods_are_public_for_both_permissions(self):
        for role in (None, *self.users):
            client = self.client_for(role)
            for url in ("/owner/", "/editor/"):
                for method in ("get", "head", "options"):
                    with self.subTest(role=role, url=url, method=method):
                        self.assertEqual(getattr(client, method)(url).status_code, 200)

    def test_owner_permission_rejects_other_roles_for_every_write(self):
        for role in (None, *self.users):
            client = self.client_for(role)
            for method in ("post", "put", "patch", "delete"):
                with self.subTest(role=role, method=method):
                    response = getattr(client, method)("/owner/", {}, format="json")
                    self.assertEqual(response.status_code, 200 if role == "owner" else 403)

    def test_editor_permission_preserves_create_update_delete_roles(self):
        allowed_methods = {
            None: set(),
            "member": set(),
            "staff": set(),
            "editor": {"put", "patch"},
            "owner": {"post", "put", "patch", "delete"},
        }
        for role, allowed in allowed_methods.items():
            client = self.client_for(role)
            for method in ("post", "put", "patch", "delete"):
                with self.subTest(role=role, method=method):
                    response = getattr(client, method)("/editor/", {}, format="json")
                    self.assertEqual(response.status_code, 200 if method in allowed else 403)

    def test_session_authentication_uses_the_logged_in_account(self):
        for role in self.users:
            with self.subTest(role=role):
                response = self.client_for(role).get("/editor/")
                self.assertEqual(response.data["username"], self.users[role].username)

    def test_session_writes_require_csrf_even_for_owner(self):
        client = self.client_for("owner", enforce_csrf=True)
        client.get("/owner/")  # Have a CSRF cookie, but omit its request header.
        for method in ("post", "put", "patch", "delete"):
            with self.subTest(method=method):
                response = getattr(client, method)("/owner/", {}, format="json")
                self.assertEqual(response.status_code, 403)
                self.assertIn("CSRF", str(response.data["detail"]))

    def test_valid_csrf_allows_owner_writes_and_editor_updates(self):
        for role, methods in (
            ("owner", ("post", "put", "patch", "delete")),
            ("editor", ("put", "patch")),
        ):
            client = self.client_for(role, enforce_csrf=True)
            token = client.get("/editor/").data["csrf_token"]
            for method in methods:
                with self.subTest(role=role, method=method):
                    response = getattr(client, method)(
                        "/editor/", {}, format="json", HTTP_X_CSRFTOKEN=token,
                    )
                    self.assertEqual(response.status_code, 200)

    def test_valid_csrf_does_not_grant_a_member_write_permission(self):
        client = self.client_for("member", enforce_csrf=True)
        token = client.get("/editor/").data["csrf_token"]
        response = client.patch("/editor/", {}, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 403)

    def test_authenticated_permission_for_star_keeps_members_allowed(self):
        anonymous = APIClient(enforce_csrf_checks=True)
        self.assertEqual(anonymous.post("/authenticated/", {}, format="json").status_code, 403)
        for role in self.users:
            with self.subTest(role=role):
                client = self.client_for(role, enforce_csrf=True)
                token = client.get("/authenticated/").data["csrf_token"]
                response = client.post(
                    "/authenticated/", {}, format="json", HTTP_X_CSRFTOKEN=token,
                )
                self.assertEqual(response.status_code, 200)
