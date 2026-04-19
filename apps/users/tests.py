from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, UserProfile, Workspace


class AuthFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def authenticate(self, email="auth@example.com", password="strongpass123", **extra):
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            **extra,
        )
        UserProfile.objects.get_or_create(user=user)
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": email,
                "password": password,
            },
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )
        return user

    def test_login_page_renders(self):
        response = self.client.get(reverse("login_page"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SeoTools AI Platform")

    def test_register_page_renders(self):
        response = self.client.get(reverse("register_page"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Account")

    def test_workspace_page_renders(self):
        response = self.client.get(reverse("workspace_home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Workspace access is connected")

    def test_register_api_creates_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "full_name": "Jane Smith",
                "email": "jane@example.com",
                "password": "strongpass123",
                "password_confirm": "strongpass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        user = CustomUser.objects.get(email="jane@example.com")
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Smith")

    def test_token_api_returns_jwt_for_registered_user(self):
        CustomUser.objects.create_user(
            email="owner@example.com",
            password="strongpass123",
        )

        response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": "owner@example.com",
                "password": "strongpass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_api_accepts_trimmed_email(self):
        CustomUser.objects.create_user(
            email="trimmed@example.com",
            password="strongpass123",
        )

        response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": "  trimmed@example.com  ",
                "password": "strongpass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_token_api_returns_unified_error_payload(self):
        CustomUser.objects.create_user(
            email="wrongpass@example.com",
            password="strongpass123",
        )

        response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": "wrongpass@example.com",
                "password": "badpass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["code"], "authentication_failed")
        self.assertIn("message", response.data)

    def test_logout_api_blacklists_refresh_token(self):
        user = CustomUser.objects.create_user(
            email="logout@example.com",
            password="strongpass123",
        )
        refresh = RefreshToken.for_user(user)

        response = self.client.post(
            reverse("token_blacklist"),
            {"refresh": str(refresh)},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_refresh_api_returns_new_access_token(self):
        user = CustomUser.objects.create_user(
            email="refresh@example.com",
            password="strongpass123",
        )
        refresh = RefreshToken.for_user(user)

        response = self.client.post(
            reverse("token_refresh"),
            {"refresh": str(refresh)},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_me_api_requires_authentication(self):
        response = self.client.get(reverse("current_user"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["code"], "not_authenticated")
        self.assertIn("message", response.data)

    def test_me_api_returns_current_user_data(self):
        user = self.authenticate(
            email="me@example.com",
            first_name="Jane",
            last_name="Smith",
        )
        response = self.client.get(reverse("current_user"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], user.email)
        self.assertEqual(response.data["full_name"], "Jane Smith")
        self.assertIn("profile", response.data)

    def test_profile_api_requires_authentication(self):
        response = self.client.get(reverse("user_profile"))

        self.assertEqual(response.status_code, 401)

    def test_profile_api_returns_current_user_profile(self):
        user = self.authenticate(
            email="profile@example.com",
            first_name="Mona",
            last_name="Ali",
            phone_number="01000000000",
        )
        user.profile.trading_goal = "Grow traffic"
        user.profile.save()

        response = self.client.get(reverse("user_profile"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "profile@example.com")
        self.assertEqual(response.data["full_name"], "Mona Ali")
        self.assertEqual(response.data["trading_goal"], "Grow traffic")

    def test_profile_api_updates_user_and_profile_fields(self):
        user = self.authenticate(email="update-profile@example.com")

        response = self.client.put(
            reverse("user_profile"),
            {
                "full_name": "Sara Ahmed",
                "phone_number": "01111111111",
                "bio": "SEO specialist",
                "timezone": "Africa/Cairo",
                "trading_goal": "Launch MVP",
                "experience_level": "advanced",
                "preferred_market": "crypto",
                "risk_appetite": "medium",
                "onboarding_completed": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        user.profile.refresh_from_db()
        self.assertEqual(user.first_name, "Sara")
        self.assertEqual(user.last_name, "Ahmed")
        self.assertEqual(user.phone_number, "01111111111")
        self.assertEqual(user.bio, "SEO specialist")
        self.assertEqual(user.timezone, "Africa/Cairo")
        self.assertEqual(user.profile.trading_goal, "Launch MVP")
        self.assertEqual(user.profile.experience_level, "advanced")
        self.assertEqual(user.profile.preferred_market, "crypto")
        self.assertEqual(user.profile.risk_appetite, "medium")
        self.assertTrue(user.profile.onboarding_completed)

    def test_register_api_returns_validation_error_shape(self):
        response = self.client.post(
            reverse("register"),
            {
                "email": "validation@example.com",
                "password": "strongpass123",
                "password_confirm": "differentpass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "validation_error")
        self.assertIn("message", response.data)
        self.assertIn("errors", response.data)

    def test_workspace_list_requires_authentication(self):
        response = self.client.get(reverse("workspace_list"))

        self.assertEqual(response.status_code, 401)

    def test_workspace_list_returns_only_current_user_workspaces(self):
        user = self.authenticate(email="workspace-owner@example.com")
        Workspace.objects.create(user=user, name="Primary Workspace")
        other_user = CustomUser.objects.create_user(
            email="other@example.com",
            password="strongpass123",
        )
        Workspace.objects.create(user=other_user, name="Other Workspace")

        response = self.client.get(reverse("workspace_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Primary Workspace")

    def test_workspace_create_persists_real_data(self):
        user = self.authenticate(email="create-workspace@example.com")

        response = self.client.post(
            reverse("workspace_list"),
            {
                "name": "SEO Team",
                "description": "Main client workspace",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        workspace = Workspace.objects.get(user=user, name="SEO Team")
        self.assertEqual(workspace.description, "Main client workspace")
        self.assertTrue(response.data["is_active"])

    def test_workspace_update_changes_owned_workspace(self):
        user = self.authenticate(email="update-workspace@example.com")
        workspace = Workspace.objects.create(
            user=user,
            name="Old Workspace",
            description="Old description",
        )

        response = self.client.put(
            reverse("workspace_detail", kwargs={"pk": workspace.pk}),
            {
                "name": "New Workspace",
                "description": "Updated description",
                "is_active": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        workspace.refresh_from_db()
        self.assertEqual(workspace.name, "New Workspace")
        self.assertEqual(workspace.description, "Updated description")
        self.assertFalse(workspace.is_active)

    def test_workspace_update_via_collection_endpoint(self):
        user = self.authenticate(email="collection-update@example.com")
        workspace = Workspace.objects.create(
            user=user,
            name="Collection Workspace",
            description="Before",
        )

        response = self.client.put(
            reverse("workspace_list"),
            {
                "id": workspace.pk,
                "name": "Collection Workspace Updated",
                "description": "After",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        workspace.refresh_from_db()
        self.assertEqual(workspace.name, "Collection Workspace Updated")

    def test_workspace_update_cannot_access_other_user_workspace(self):
        self.authenticate(email="self@example.com")
        other_user = CustomUser.objects.create_user(
            email="owner2@example.com",
            password="strongpass123",
        )
        workspace = Workspace.objects.create(user=other_user, name="Private Workspace")

        response = self.client.put(
            reverse("workspace_detail", kwargs={"pk": workspace.pk}),
            {
                "name": "Hacked Workspace",
                "description": "",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 404)
