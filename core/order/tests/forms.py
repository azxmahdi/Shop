from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from accounts.models import UserType
from order.forms import CheckOutForm

User = get_user_model()


class CheckOutFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com",
            password="User123/",
            type=UserType.customer.value,
        )
        cls.request = MagicMock()
        cls.request.user = cls.user

    @patch("order.forms.CouponModel.objects")
    def test_form_With_the_wrong_ID_address(self, mock_coupon_manager):
        mock_coupon = MagicMock()
        mock_coupon.used_by.count.return_value = 2
        mock_coupon.max_limit_usage = 4
        mock_coupon.expiration_date = timezone.now() + timedelta(days=2)
        mock_coupon_manager.get.return_value = mock_coupon

        data = {"address_id": 999, "coupon": "Mycode"}
        form = CheckOutForm(data=data)
        form.request = self.request
        self.assertFalse(form.is_valid())
        self.assertIn(
            "آدرس نامعتبر برای کاربر درخواست شده.", form.errors["address_id"]
        )

    @patch("order.forms.UserAddressModel.objects")
    def test_coupon_do_not_exists(self, mock_address_manager):
        mock_address_manager.get.return_value = MagicMock()
        data = {"address_id": 1, "coupon": "InvalidCode"}
        form = CheckOutForm(data=data)
        self.request.user = self.user
        form.request = self.request
        self.assertFalse(form.is_valid())
        self.assertIn("کد تخفیف اشتباه است", form.errors["coupon"])
        mock_address_manager.get.assert_called_once_with(id=1, user=self.user)

    @patch("order.forms.UserAddressModel.objects")
    @patch("order.forms.CouponModel.objects")
    def test_coupon_usage_limit_exceeded(
        self, mock_coupon_manager, mock_address_manager
    ):
        mock_coupon = MagicMock()
        mock_coupon.used_by.count.return_value = 4
        mock_coupon.max_limit_usage = 4

        mock_coupon_manager.get.return_value = mock_coupon

        mock_address_manager.get.return_value = MagicMock()

        data = {"address_id": 1, "coupon": "InvalidCode"}
        form = CheckOutForm(data=data)
        form.request = self.request
        self.assertFalse(form.is_valid())
        self.assertIn("محدودیت در تعداد استفاده", form.errors["coupon"])
        mock_coupon_manager.get.assert_called_once_with(code="InvalidCode")
        mock_address_manager.get.assert_called_once_with(id=1, user=self.user)

    @patch("order.forms.UserAddressModel.objects")
    @patch("order.forms.CouponModel.objects")
    def test_coupon_expired(self, mock_coupon_manager, mock_address_manager):
        mock_coupon = MagicMock()
        mock_coupon.used_by.count.return_value = 2
        mock_coupon.max_limit_usage = 4
        mock_coupon.expiration_date = timezone.now() - timedelta(days=1)
        mock_coupon_manager.get.return_value = mock_coupon

        mock_address_manager.get.return_value = MagicMock()

        data = {"address_id": 1, "coupon": "InvalidCode"}

        form = CheckOutForm(data=data)
        form.request = self.request
        self.assertFalse(form.is_valid())
        self.assertIn("کد تخفیف منقضی شده است", form.errors["coupon"])
        mock_coupon_manager.get.assert_called_once_with(code="InvalidCode")
        mock_address_manager.get.assert_called_once_with(id=1, user=self.user)

    @patch("order.forms.UserAddressModel.objects")
    @patch("order.forms.CouponModel.objects")
    def test_coupon_used(self, mock_coupon_manager, mock_address_manager):
        self.client.force_login(self.user)
        mock_coupon = MagicMock()
        mock_coupon.used_by.count.return_value = 2
        mock_coupon.max_limit_usage = 4
        mock_coupon.expiration_date = timezone.now() + timedelta(days=2)
        mock_coupon.used_by.all.return_value = [
            self.user,
        ]
        mock_coupon_manager.get.return_value = mock_coupon

        mock_address_manager.get.return_value = MagicMock()

        data = {"address_id": 1, "coupon": "InvalidCode"}

        form = CheckOutForm(data=data)
        form.request = self.request
        self.assertFalse(form.is_valid())
        self.assertIn(
            "این کد تخفیف قبلا توسط شما استفاده شده است", form.errors["coupon"]
        )
        mock_coupon_manager.get.assert_called_once_with(code="InvalidCode")
        mock_address_manager.get.assert_called_once_with(id=1, user=self.user)

    @patch("order.forms.UserAddressModel.objects")
    @patch("order.forms.CouponModel.objects")
    def test_valid_coupon_success(
        self, mock_coupon_manager, mock_address_manager
    ):

        mock_coupon = MagicMock()
        mock_coupon.used_by.count.return_value = 2
        mock_coupon.max_limit_usage = 4
        mock_coupon.expiration_date = timezone.now() + timedelta(days=2)
        mock_coupon.discount_percent = 20

        mock_coupon_manager.get.return_value = mock_coupon

        mock_address_manager.get.return_value = MagicMock()

        data = {"address_id": 1, "coupon": "ValidCode"}

        form = CheckOutForm(data=data)
        form.request = self.request
        self.assertTrue(form.is_valid())
        mock_coupon_manager.get.assert_called_once_with(code="ValidCode")
        mock_address_manager.get.assert_called_once_with(id=1, user=self.user)
