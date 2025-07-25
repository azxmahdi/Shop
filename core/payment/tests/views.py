from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from order.models import OrderModel, OrderStatusType
from payment.models import PaymentModel, PaymentStatusType

User = get_user_model()


class PaymentVerifyViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
        )
        self.payment = PaymentModel.objects.create(
            authority_id="123456789", amount=100
        )

        self.order = OrderModel.objects.create(
            user=self.user,
            address="test address",
            state="test state",
            city="test city",
            zip_code="12345",
            total_price=100,
            payment=self.payment,
            coupon=None,
            status=OrderStatusType.pending.value,
        )

        self.url = reverse("payment:verify")

    @patch("payment.views.ZarinPalSandbox")
    def test_successful_payment_verification(self, MockZarinPalSandbox):
        mock_zarinpal_instance = MockZarinPalSandbox.return_value
        mock_zarinpal_instance.payment_verify.return_value = {
            "Status": 100,
            "RefID": 54321,
            "Message": "Success",
        }
        data = {"Authority": "123456789", "Status": "OK"}

        response = self.client.get(self.url, data)

        self.assertEqual(response.url, reverse_lazy("order:completed"))

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.ref_id, 54321)
        self.assertEqual(self.payment.response_code, 100)
        self.assertEqual(self.payment.status, PaymentStatusType.success.value)
        self.assertEqual(
            self.payment.response_json,
            {"Status": 100, "RefID": 54321, "Message": "Success"},
        )

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatusType.success.value)

    @patch("payment.views.ZarinPalSandbox")
    def test_failed_payment_verification(self, MockZarinPalSandbox):
        mock_zarinpal_instance = MockZarinPalSandbox.return_value
        mock_zarinpal_instance.payment_verify.return_value = {
            "Status": -21,
            "RefID": None,
            "Message": "Failed",
        }
        data = {"Authority": "123456789", "Status": "NOK"}
        response = self.client.get(self.url, data)
        self.assertEqual(response.url, reverse_lazy("order:failed"))

        self.payment.refresh_from_db()
        self.assertIsNone(self.payment.ref_id)
        self.assertEqual(self.payment.response_code, -21)
        self.assertEqual(self.payment.status, PaymentStatusType.failed.value)
        self.assertEqual(self.payment.response_json["Status"], -21)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatusType.failed.value)
