from django.test import TestCase

from ..models import PaymentModel, PaymentStatusType


class TestOrderStatusType(TestCase):
    def test_choices_structure(self):
        expected_choices = [
            (1, "در انتظار"),
            (2, "پرداخت موفق"),
            (3, "پرداخت ناموفق"),
        ]
        self.assertEqual(expected_choices, PaymentStatusType.choices)


class TestPayment(TestCase):
    def test_payment_creation(self):
        payment = PaymentModel.objects.create(
            authority_id="123456789",
            amount=100,
            response_json={"status": "success"},
            response_code=100,
            status=PaymentStatusType.success.value,
        )
        self.assertEqual(payment.authority_id, "123456789")
        self.assertEqual(payment.amount, 100)
        self.assertEqual(payment.response_json, {"status": "success"})
        self.assertEqual(payment.response_code, 100)
        self.assertEqual(payment.status, PaymentStatusType.success.value)
