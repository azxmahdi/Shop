from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile

User = get_user_model()


class CustomerSecurityEditViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
        )
        cls.data = {
            "old_password": "User123/",
            "new_password": "NewPassword123/",
            "confirm_password": "NewPassword123/",
        }

        cls.url = reverse("dashboard:customer:security-edit")

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_changed_with_wrong_password(self):
        self.client.force_login(self.user)
        data = self.data.copy()
        data["old_password"] = "WrongPassword"
        response = self.client.post(path=self.url, data=data, follow=True)
        self.user.refresh_from_db()

        self.assertContains(
            response, "پسورد قبلی شما اشتباه وارد شده است، لطفا تصحیح نمایید"
        )
        self.assertFalse(self.user.check_password(data["old_password"]))

    def test_changed_with_right_password(self):
        self.client.force_login(self.user)

        response = self.client.post(path=self.url, data=self.data, follow=True)
        self.user.refresh_from_db()
        self.assertContains(response, "رمز عبور با موفقیت تغییر یافت")
        self.assertTrue(self.user.check_password(self.data["new_password"]))

    def test_changed_password_with_invalid_data(self):
        self.client.force_login(self.user)
        data = self.data.copy()
        data["new_password"] = ""
        response = self.client.post(path=self.url, data=data, follow=True)
        self.user.refresh_from_db()

        self.assertContains(response, "لطفا اطلاعات را به درستی وارد کنید.")
        self.assertFalse(self.user.check_password(data["new_password"]))


class CustomerProfileEditTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="test@example.com", password="Test123/"
        )

        cls.profile = Profile.objects.get(user=cls.user)
        cls.profile.first_name = "first name"
        cls.profile.last_name = "lats name"
        cls.profile.save()

        cls.url = reverse("dashboard:customer:profile-edit")

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_profile_edit_with_valid_data(self):
        self.client.force_login(self.user)
        data = {
            "first_name": "first name updated",
            "last_name": "last name updated",
            "phone_number": "09999999999",
            "image": "image.jpg",
        }

        response = self.client.post(path=self.url, data=data, follow=True)

        self.profile.refresh_from_db()

        self.assertContains(response, "بروز رسانی پروفایل با موفقیت انجام شد")
        self.assertEqual(self.profile.first_name, "first name updated")
