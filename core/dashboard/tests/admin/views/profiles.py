from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile, UserType

User = get_user_model()


class AdminSecurityEditViewTest(TestCase):
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

        cls.url = reverse("dashboard:admin:security-edit")

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

    def test_change_password_with_valid_data(self):
        self.client.force_login(self.admin)
        data = {
            "old_password": "Admin123/",
            "new_password": "NewAdmin123/",
            "confirm_password": "NewAdmin123/",
        }
        response = self.client.post(self.url, data, follow=True)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password("NewAdmin123/"))
        self.assertFalse(self.admin.check_password("Admin123/"))
        self.assertContains(response, "رمز عبور با موفقیت تغییر یافت")

    def test_check_password_invalid_data(self):
        self.client.force_login(self.admin)
        data = {
            "old_password": "Invalid password",
            "new_password": "NewAdmin123/",
            "confirm_password": "NewAdmin123/",
        }
        response = self.client.post(self.url, data, follow=True)
        self.admin.refresh_from_db()
        self.assertFalse(self.admin.check_password("NewAdmin123/"))
        self.assertTrue(self.admin.check_password("Admin123/"))
        self.assertContains(
            response, "پسورد قبلی شما اشتباه وارد شده است، لطفا تصحیح نمایید."
        )


class AdminProfileEditViewTest(TestCase):
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
        profile = Profile.objects.get(user=cls.user)
        profile.first_name = "first name"
        profile.last_name = "lats name"
        profile.save()

        cls.url = reverse("dashboard:admin:profile-edit")

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

    def test_profile_edit_with_valid_data(self):
        self.client.force_login(self.admin)
        data = {
            "first_name": "first name updated",
            "last_name": "last name updated",
            "phone_number": "09999999999",
            "image": "image.jpg",
        }

        response = self.client.post(self.url, data, follow=True)

        profile = Profile.objects.get(user=self.admin)

        self.assertContains(response, "بروز رسانی پروفایل با موفقیت انجام شد")
        self.assertEqual(profile.first_name, "first name updated")
