from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserType
from order.models import OrderModel, OrderStatusType
from payment.models import PaymentModel, PaymentStatusType

User = get_user_model()


class AdminOrderListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            email="test@example.com", password="Test123/"
        )
        cls.user1.user_profile.first_name = "first_name_1"
        cls.user1.user_profile.last_name = "last_name_1"
        cls.user1.user_profile.save()
        cls.user1.refresh_from_db()

        cls.user2 = User.objects.create_user(
            email="test2@example.com", password="Test123/"
        )
        cls.user2.user_profile.first_name = "first_name_2"
        cls.user2.user_profile.last_name = "last_name_2"
        cls.user2.user_profile.save()
        cls.user2.refresh_from_db()

        cls.admin = User.objects.create_user(
            email="admin@example.com",
            password="Admin123/",
            type=UserType.admin.value,
        )

        cls.payment = PaymentModel.objects.create(
            authority_id="123456789",
            amount=100,
            response_json={"status": "success"},
            response_code=100,
            status=PaymentStatusType.success.value,
        )

        cls.order1 = OrderModel.objects.create(
            user=cls.user1,
            address="test address",
            state="test state",
            city="test city",
            zip_code="12345",
            total_price=1,
            payment=cls.payment,
            coupon=None,
            status=OrderStatusType.pending.value,
        )

        cls.order2 = OrderModel.objects.create(
            user=cls.user2,
            address="test address",
            state="test state",
            city="test city",
            zip_code="12345",
            total_price=2,
            payment=cls.payment,
            coupon=None,
            status=OrderStatusType.pending.value,
        )

        cls.url = reverse("dashboard:admin:order-list")

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_admin_user(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order1.total_price)

    def test_search_functionality(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url + "?q=first_name_1")

        self.assertContains(response, self.order1.user.user_profile.first_name)
        self.assertNotContains(
            response, self.order2.user.user_profile.first_name
        )


class AdminOrderDetailViewTest(TestCase):
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

        cls.payment = PaymentModel.objects.create(
            authority_id="123456789",
            amount=100,
            response_json={"status": "success"},
            response_code=100,
            status=PaymentStatusType.success.value,
        )

        cls.order = OrderModel.objects.create(
            user=cls.user,
            address="test address",
            state="test state",
            city="test city",
            zip_code="12345",
            total_price=1,
            payment=cls.payment,
            coupon=None,
            status=OrderStatusType.pending.value,
        )

        cls.url = reverse("dashboard:admin:order-detail", args=[cls.order.pk])

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
        self.assertContains(response, self.order.total_price)


class AdminOrderInvoiceViewTest(TestCase):
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

        cls.payment = PaymentModel.objects.create(
            authority_id="123456789",
            amount=100,
            response_json={"status": "success"},
            response_code=100,
            status=PaymentStatusType.success.value,
        )

        cls.success_order = OrderModel.objects.create(
            user=cls.user,
            status=OrderStatusType.success.value,
            payment=cls.payment,
            total_price=10000,
            address="Test Address",
        )

        cls.pending_order = OrderModel.objects.create(
            user=cls.user,
            status=OrderStatusType.pending.value,
            payment=cls.payment,
            total_price=20000,
            address="Test Address",
        )
        cls.url_success_order = reverse(
            "dashboard:admin:order-invoice", args=[cls.success_order.pk]
        )
        cls.url_pending_order = reverse(
            "dashboard:admin:order-invoice", args=[cls.pending_order.pk]
        )

    def test_non_success_order_returns_404(self):
        self.client.force_login(self.admin)

        response = self.client.get(self.url_pending_order)
        self.assertEqual(response.status_code, 404)

    def test_success_order_returns_200(self):
        self.client.force_login(self.admin)

        response = self.client.get(self.url_success_order)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user(self):
        response = self.client.get(self.url_success_order)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_success_order)
        self.assertEqual(response.status_code, 403)

    def test_admin_user(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url_success_order)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.success_order.total_price)
