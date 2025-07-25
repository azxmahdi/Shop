from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from order.models import OrderModel, OrderStatusType
from payment.models import PaymentModel, PaymentStatusType

User = get_user_model()


class CustomerOrderListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            email="user1@gmail.com", password="User123/"
        )
        cls.user2 = User.objects.create_user(
            email="user2@gmail.com", password="User123/"
        )
        cls.payment1 = PaymentModel.objects.create(
            authority_id="123456789",
            amount=100,
            response_json={"status": "success"},
            response_code=100,
            status=PaymentStatusType.success.value,
        )
        cls.payment2 = PaymentModel.objects.create(
            authority_id="987654321",
            amount=200,
            response_json={"status": "success"},
            response_code=100,
            status=PaymentStatusType.success.value,
        )

        cls.order1 = OrderModel.objects.create(
            user=cls.user1,
            address="test address 1",
            state="test state 1",
            city="test city 1",
            zip_code="12345 1",
            total_price=10000,
            payment=cls.payment1,
            coupon=None,
            status=OrderStatusType.success.value,
        )

        cls.order2 = OrderModel.objects.create(
            user=cls.user2,
            address="test address 2",
            state="test state 2",
            city="test city 2",
            zip_code="12345 2",
            total_price=200000,
            payment=cls.payment2,
            coupon=None,
            status=OrderStatusType.pending.value,
        )

        cls.url = reverse("dashboard:customer:order-list")

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order1.get_price())
        self.assertNotContains(response, self.order2.get_price())

    def test_search_functionality(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url + f"?q={str(self.order1.id)}")

        self.assertContains(response, self.order1.get_price())
        self.assertNotContains(response, self.order2.get_price())

    def test_context_data(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(
            response.context["total_items"],
            OrderModel.objects.filter(user=self.user1).count(),
        )
        self.assertEqual(
            response.context["status_types"], OrderStatusType.choices
        )


class CustomerOrderDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            email="user1@gmail.com", password="User123/"
        )
        cls.user2 = User.objects.create_user(
            email="user2@gmail.com", password="User123/"
        )
        cls.payment1 = PaymentModel.objects.create(
            authority_id="123456789",
            amount=100,
            response_json={"status": "success"},
            response_code=100,
            status=PaymentStatusType.success.value,
        )
        cls.payment2 = PaymentModel.objects.create(
            authority_id="987654321",
            amount=200,
            response_json={"status": "success"},
            response_code=100,
            status=PaymentStatusType.success.value,
        )

        cls.order1 = OrderModel.objects.create(
            user=cls.user1,
            address="test address 1",
            state="test state 1",
            city="test city 1",
            zip_code="12345 1",
            total_price=10000,
            payment=cls.payment1,
            coupon=None,
            status=OrderStatusType.success.value,
        )

        cls.order2 = OrderModel.objects.create(
            user=cls.user2,
            address="test address 2",
            state="test state 2",
            city="test city 2",
            zip_code="12345 2",
            total_price=200000,
            payment=cls.payment2,
            coupon=None,
            status=OrderStatusType.pending.value,
        )

        cls.url = reverse(
            "dashboard:customer:order-detail", kwargs={"pk": cls.order1.pk}
        )

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order1.get_price())

    def test_get_queryset(self):
        self.client.force_login(self.user1)
        url = reverse(
            "dashboard:customer:order-detail", kwargs={"pk": self.order2.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class CustomerOrderInvoiceViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            email="user1@gmail.com", password="User123/"
        )
        cls.user2 = User.objects.create_user(
            email="user2@gmail.com", password="User123/"
        )
        cls.payment1 = PaymentModel.objects.create(
            authority_id="123456789",
            amount=100,
            response_json={"status": "success"},
            response_code=100,
            status=PaymentStatusType.success.value,
        )
        cls.payment2 = PaymentModel.objects.create(
            authority_id="987654321",
            amount=200,
            response_json={"status": "success"},
            response_code=100,
            status=PaymentStatusType.success.value,
        )

        cls.order1 = OrderModel.objects.create(
            user=cls.user1,
            address="test address 1",
            state="test state 1",
            city="test city 1",
            zip_code="12345 1",
            total_price=10000,
            payment=cls.payment1,
            coupon=None,
            status=OrderStatusType.success.value,
        )

        cls.order2 = OrderModel.objects.create(
            user=cls.user2,
            address="test address 2",
            state="test state 2",
            city="test city 2",
            zip_code="12345 2",
            total_price=200000,
            payment=cls.payment2,
            coupon=None,
            status=OrderStatusType.success.value,
        )

        cls.url = reverse(
            "dashboard:customer:order-invoice", kwargs={"pk": cls.order1.pk}
        )

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order1.get_price())

    def test_get_queryset(self):
        self.client.force_login(self.user1)
        url = reverse(
            "dashboard:customer:order-detail", kwargs={"pk": self.order2.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.order1.status = OrderStatusType.pending.value
        self.order1.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
