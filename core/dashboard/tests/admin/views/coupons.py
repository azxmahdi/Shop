from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import UserType
from order.models import CouponModel

User = get_user_model()


class AdminCouponListViewTest(TestCase):
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
        cls.coupon1 = CouponModel.objects.create(
            user=cls.admin, code="Coupon Test 1", discount_percent=30
        )
        cls.coupon2 = CouponModel.objects.create(
            user=cls.admin, code="Coupon Test 2", discount_percent=50
        )
        cls.url = reverse("dashboard:admin:coupon-list")

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
        self.assertContains(response, self.coupon1.code)
        self.assertContains(response, self.coupon2.code)


class AdminCouponCreateViewTest(TestCase):
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

        cls.url = reverse("dashboard:admin:coupon-create")

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

    def test_creation(self):
        self.client.force_login(self.admin)
        now = timezone.now()
        data = {
            "code": "Test Coupon",
            "discount_percent": 30,
            "max_limit_usage": 10,
            "expiration_date": now + timedelta(weeks=1),
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(response, "ایجاد کد تخفیف با موفقیت انجام شد")
        self.assertTrue(
            CouponModel.objects.filter(code="Test Coupon").exists()
        )


class AdminCouponEditViewTest(TestCase):
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
        cls.coupon = CouponModel.objects.create(
            user=cls.admin, code="Coupon Test", discount_percent=30
        )
        cls.url = reverse("dashboard:admin:coupon-edit", args=[cls.coupon.pk])

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

    def test_edit(self):
        self.assertEqual(self.coupon.code, "Coupon Test")
        self.client.force_login(self.admin)
        now = timezone.now()
        data = {
            "code": "Coupon Test Edited",
            "discount_percent": 30,
            "max_limit_usage": 10,
            "expiration_date": now + timedelta(weeks=1),
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(response, "ویرایش کد تخفیف با موفقیت انجام شد")
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.code, "Coupon Test Edited")


class AdminCouponDeleteViewTest(TestCase):
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
        cls.coupon = CouponModel.objects.create(
            user=cls.admin, code="Coupon Test", discount_percent=30
        )
        cls.url = reverse(
            "dashboard:admin:coupon-delete", args=[cls.coupon.pk]
        )

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

    def test_delete(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, follow=True)
        self.assertContains(response, "حذف کد تخفیف با موفقیت انجام شد")
        self.assertFalse(
            CouponModel.objects.filter(code=self.coupon.code).exists()
        )
