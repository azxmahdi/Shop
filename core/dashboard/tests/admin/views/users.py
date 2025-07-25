from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserType

User = get_user_model()


class AdminUserListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="test@example.com", password="Test123/"
        )
        cls.admin = User.objects.create_user(
            email="admin@example.com",
            password="Admin123/",
            type=UserType.admin.value,
        )

        cls.url = reverse("dashboard:admin:user-list")

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_admin_user(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)

    def test_search_functionality(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url + "?q=sdmin@example.com")
        self.assertContains(response, self.admin.email)
        self.assertNotContains(response, self.user.email)

    def test_context_data(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(
            response.context["total_items"],
            User.objects.exclude(email=self.admin.email).count(),
        )


class AdminUserUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="test@example.com",
            password="Test123/",
            type=UserType.customer.value,
        )
        cls.admin = User.objects.create_user(
            email="admin@example.com",
            password="Admin123/",
            type=UserType.admin.value,
        )
        cls.superuser = User.objects.create_superuser(
            email="superuser@example.com", password="Test123/"
        )
        cls.url = reverse(
            "dashboard:admin:user-edit", kwargs={"pk": cls.user.id}
        )

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_admin_user(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_update_data(self):
        self.client.force_login(self.superuser)

        data = {
            "email": self.user.email,
            "type": UserType.admin.value,
            "is_active": True,
            "is_verified": True,
        }

        self.client.post(self.url, data)

        self.user.refresh_from_db()

        self.assertEqual(self.admin.type, UserType.admin.value)
        self.assertTrue(self.admin.is_active)


class AdminUserDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="test@example.com",
            password="Test123/",
            type=UserType.customer.value,
        )
        cls.admin = User.objects.create_user(
            email="admin@example.com",
            password="Admin123/",
            type=UserType.admin.value,
        )
        cls.superuser = User.objects.create_superuser(
            email="superuser@example.com", password="Test123/"
        )
        cls.url = reverse(
            "dashboard:admin:user-delete", kwargs={"pk": cls.user.id}
        )

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)

    def test_admin_user(self):
        self.client.force_login(self.admin)
        self.client.post(self.url)
        self.assertFalse(User.objects.filter(email=self.user.email).exists())
