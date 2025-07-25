from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from ..views import generate_activation_token, verify_activation_token

User = get_user_model()


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="test123"
        )

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            reverse("accounts:login"),
            data={"email": self.user.email, "password": "test123"},
        )
        self.assertRedirects(response, reverse("website:index"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_invalid_credentials(self):
        response = self.client.post(
            reverse("accounts:login"),
            data={"email": self.user.email, "password": "invalid_password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "اطلاعات وارد شده درست نیست")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_with_user_inactive(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            reverse("accounts:login"),
            data={"email": self.user.email, "password": "test123"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "حساب کاربری شما غیر فعال شده است. لطفا با پشتیبانی تماس بگیرید.",
        )
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class SignUpViewTest(TestCase):
    def test_sign_up_with_valid_credentials(self):
        response = self.client.post(
            reverse("accounts:sign-up"),
            data={
                "email": "test@example.com",
                "password": "Test123/",
                "confirm_password": "Test123/",
            },
        )
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_sign_up_with_invalid_password(self):
        response = self.client.post(
            reverse("accounts:sign-up"),
            data={
                "email": "test@example.com",
                "password": "Test1234/",
                "confirm_password": "Test123/",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "رمز عبور جدید و تأییدیه آن مطابقت ندارند."
        )
        self.assertFalse(
            User.objects.filter(email="test@example.com").exists()
        )

    def test_sign_up_with_user_created(self):
        User.objects.create_user(email="test@example.com", password="test123")

        response = self.client.post(
            reverse("accounts:sign-up"),
            data={
                "email": "test@example.com",
                "password": "Test123/",
                "confirm_password": "Test123/",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "کاربری با ایمیل وارد شده وجود دارد.")


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="test123"
        )
        self.client.login(email=self.user.email, password="test123")

    def test_logout(self):
        response = self.client.get(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("website:index"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class SendMailResetPasswordViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="testuser@example.com",
            password="test123",
        )
        cls.reset_url = reverse("accounts:send-mail-reset-password")

    def test_send_mail_reset_password(self):
        response = self.client.post(
            self.reset_url, data={"email": self.user.email}, follow=True
        )
        self.assertRedirects(
            response, reverse("accounts:send-mail-reset-password")
        )
        self.assertContains(response, "لطفا ایمیل خود را چک کنید")

    def test_send_mail_reset_password_with_invalid_email(self):
        response = self.client.post(
            self.reset_url,
            data={"email": "invalid_email@gmail.com"},
            follow=True,
        )
        self.assertRedirects(
            response, reverse("accounts:send-mail-reset-password")
        )
        self.assertContains(response, "کاربری با این ایمیل وجود ندارد")

    def test_send_mail_reset_password_with_user_not_active(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(
            self.reset_url, data={"email": self.user.email}, follow=True
        )
        self.assertRedirects(
            response, reverse("accounts:send-mail-reset-password")
        )
        self.assertContains(
            response,
            "حساب کاربری شما غیر فعال شده است. لطفا با پشتیبانی تماس بگیرید.",
        )


class RestPasswordViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="old_password", is_active=True
        )
        self.token = generate_activation_token(self.user.email)

    def test_valid_token_get_request(self):
        response = self.client.get(
            reverse("accounts:reset-password", args=[self.token])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")

    def test_invalid_token_get_request(self):
        response = self.client.get(
            reverse("accounts:reset-password", args=["invalid-token"])
        )
        self.assertContains(response, "زمان تغییر پسورد به پایان رسیده است")

    def test_valid_password_change(self):
        response = self.client.post(
            reverse("accounts:reset-password", args=[self.token]),
            {"password": "Test123/", "confirm_password": "Test123/"},
            follow=True,
        )
        self.assertRedirects(response, reverse("accounts:login"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Test123/"))

    def test_password_mismatch(self):
        response = self.client.post(
            reverse("accounts:reset-password", args=[self.token]),
            {"password": "Test123/", "confirm_password": "Test123456/"},
        )
        self.assertContains(
            response, "رمز عبور جدید و تأییدیه آن مطابقت ندارند"
        )

    def test_expired_token(self):
        expired_token = generate_activation_token(self.user.email)
        email = verify_activation_token(expired_token, expiration=-1)
        self.assertIsNone(email)


class TokenUtilsTest(TestCase):
    def test_token_generation_and_verification(self):
        email = "test@example.com"
        token = generate_activation_token(email)
        decoded_email = verify_activation_token(token)
        self.assertEqual(decoded_email, email)

    def test_invalid_token_verification(self):
        decoded_email = verify_activation_token("invalid-token")
        self.assertIsNone(decoded_email)
