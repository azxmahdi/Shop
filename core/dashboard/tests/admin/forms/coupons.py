import datetime

from django.test import TestCase
from django.utils import timezone

from dashboard.admin.forms import CouponForm


class AdminCouponFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_data = {
            "code": "test_code",
            "discount_percent": 20,
            "max_limit_usage": 10,
            "expiration_date": timezone.now() + datetime.timedelta(days=5),
        }
        cls.form = CouponForm(cls.valid_data)

    def test_coupon_form_with_valid_data(self):
        self.assertTrue(self.form.is_valid())

    def test_coupon_form_with_invalid_data(self):
        invalid_data = self.valid_data.copy()
        invalid_data["code"] = ""
        form = CouponForm(invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("code", form.errors)
