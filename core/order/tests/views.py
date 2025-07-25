import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from cart.models import CartItemModel, CartModel
from order.models import (
    CouponModel,
    OrderItemModel,
    OrderModel,
    UserAddressModel,
)
from payment.models import PaymentModel
from shop.models import ProductCategoryModel, ProductModel, ProductStatusType

User = get_user_model()


class OrderCheckOutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
        )
        self.client.force_login(self.user)
        CartModel.objects.filter(user=self.user).delete()
        self.cart = CartModel.objects.create(user=self.user)
        self.category = ProductCategoryModel.objects.create(
            title="Category test", slug="category-test"
        )
        self.product1 = ProductModel.objects.create(
            user=self.user,
            category=self.category,
            title="Product test 1",
            slug="product-test-1",
            description="This is description 1",
            stock=15,
            price=100,
            status=ProductStatusType.publish.value,
        )
        self.product2 = ProductModel.objects.create(
            user=self.user,
            category=self.category,
            title="Product test 2",
            slug="product-test-2",
            description="This is description 2",
            stock=10,
            price=200,
            status=ProductStatusType.publish.value,
        )
        self.cart_item1 = CartItemModel.objects.create(
            cart=self.cart, product=self.product1, quantity=10
        )
        self.cart_item2 = CartItemModel.objects.create(
            cart=self.cart, product=self.product2, quantity=5
        )
        self.address = UserAddressModel.objects.create(
            user=self.user,
            address="My address",
            state="My state",
            city="My city",
            zip_code="1234",
        )
        self.coupon = CouponModel.objects.create(
            code="Coupon Test", discount_percent=20
        )
        self.mock_zarinpal_patcher = patch("order.views.ZarinPalSandbox")
        self.mock_zarinpal_class = self.mock_zarinpal_patcher.start()
        self.mock_zarinpal_instance = MagicMock()
        self.mock_zarinpal_class.return_value = self.mock_zarinpal_instance
        self.mock_zarinpal_instance.payment_request.return_value = {
            "data": {"authority": "mock_authority_123"}
        }
        self.mock_zarinpal_instance.generate_payment_url.return_value = (
            "http://mock.zarinpal.com/payment/start/mock_authority_123"
        )

        self.mock_validate_quantity_in_cart_summer_patcher = patch(
            "order.views.validate_quantity_in_cart_summer"
        )
        self.mock_validate_quantity_in_cart_summer_class = (
            self.mock_validate_quantity_in_cart_summer_patcher.start()
        )
        self.mock_validate_quantity_in_cart_summer_instance = {
            "status": "ok",
            "message": "سبد خرید با موفقیت آماده شد.",
        }
        self.mock_validate_quantity_in_cart_summer_class.return_value = (
            self.mock_validate_quantity_in_cart_summer_instance
        )

        self.mock_cart_session_patcher = patch("order.views.CartSession")
        self.mock_cart_session_class = self.mock_cart_session_patcher.start()
        self.mock_cart_session_instance = MagicMock()
        self.mock_cart_session_class.return_value = (
            self.mock_cart_session_instance
        )

        self.mock_cart_session_signal_patcher = patch(
            "cart.signals.CartSession"
        )
        self.mock_cart_session_signal_class = (
            self.mock_cart_session_signal_patcher.start()
        )
        self.mock_cart_session_signal_instance = MagicMock()
        self.mock_cart_session_signal_instance.sync_cart_items_from_db.return_value = (
            MagicMock()
        )
        self.mock_cart_session_signal_instance.merge_session_cart_in_db.return_value = (
            MagicMock()
        )
        self.mock_cart_session_signal_class.return_value = (
            self.mock_cart_session_signal_instance
        )

        self.cart_summary_url = reverse("cart:cart-summary")
        self.checkout_url = reverse("order:checkout")
        self.success_url = (
            "http://mock.zarinpal.com/payment/start/mock_authority_123"
        )

    def tearDown(self):
        self.mock_cart_session_patcher.stop()
        self.mock_validate_quantity_in_cart_summer_patcher.stop()
        self.mock_zarinpal_patcher.stop()
        self.mock_cart_session_signal_patcher.stop()

    def test_anonymous_user(self):
        self.client.logout()
        response = self.client.get(self.checkout_url)
        self.assertEqual(response.status_code, 302)

    def test_post_checkout_success_no_coupon(self):
        initial_order_count = OrderModel.objects.count()
        initial_order_item_count = OrderItemModel.objects.count()
        initial_payment_count = PaymentModel.objects.count()

        form_data = {
            "address_id": self.address.id,
            "coupon": "",
        }
        response = self.client.post(self.checkout_url, form_data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.url.startswith("http://mock.zarinpal.com/payment/start/")
        )

        self.assertEqual(OrderModel.objects.count(), initial_order_count + 1)

        order = OrderModel.objects.latest("id")
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.address, self.address.address)
        self.assertEqual(order.total_price, Decimal("2000"))
        self.assertIsNone(order.coupon)

        self.assertEqual(
            OrderItemModel.objects.count(), initial_order_item_count + 2
        )
        self.assertEqual(order.order_items.count(), 2)
        self.assertTrue(
            order.order_items.filter(
                product=self.product1, quantity=10, price=self.product1.price
            ).exists()
        )
        self.assertTrue(
            order.order_items.filter(
                product=self.product2, quantity=5, price=self.product2.price
            ).exists()
        )

        self.assertEqual(
            PaymentModel.objects.count(), initial_payment_count + 1
        )
        payment = PaymentModel.objects.latest("id")
        self.assertEqual(payment.authority_id, "mock_authority_123")
        self.assertEqual(payment.amount, Decimal("2000"))
        self.assertEqual(order.payment, payment)

        self.assertEqual(self.cart.cart_items.count(), 0)
        self.mock_cart_session_instance.clear.assert_called_once()

        self.mock_validate_quantity_in_cart_summer_class.assert_called_once_with(
            response.wsgi_request
        )
        self.mock_zarinpal_instance.payment_request.assert_called_once_with(
            Decimal("2000")
        )
        self.mock_zarinpal_instance.generate_payment_url.assert_called_once_with(
            "mock_authority_123"
        )

    def test_post_checkout_success_with_coupon(self):
        data = {"address_id": self.address.id, "coupon": self.coupon.code}
        response = self.client.post(self.checkout_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.url.startswith("http://mock.zarinpal.com/payment/start/")
        )
        order = OrderModel.objects.latest("id")
        self.assertEqual(order.coupon.id, self.coupon.id)

        self.mock_zarinpal_instance.payment_request.assert_called_once_with(
            Decimal("1600")
        )

    def test_post_checkout_quantity_warning(self):
        self.mock_validate_quantity_in_cart_summer_class.return_value = {
            "status": "warning",
            "message": "از آنجایی که تعداد موجودی برخی از محصولات کمتر از تعداد موجودی شما است. تعداد آنها به حداکثر موجودی تغییر یافت",
        }

        initial_order_count = OrderModel.objects.count()

        form_data = {"address_id": self.address.id, "coupon": ""}
        response = self.client.post(self.checkout_url, form_data)
        self.assertEqual(OrderModel.objects.count(), initial_order_count)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "از آنجایی که تعداد موجودی برخی از محصولات کمتر از تعداد موجودی شما است. تعداد آنها به حداکثر موجودی تغییر یافت",
        )

        self.mock_zarinpal_class.generate_payment_url.assert_not_called()

    def test_post_checkout_with_invalid_data(self):
        initial_order_count = OrderModel.objects.count()

        form_data = {"address_id": 9999, "coupon": ""}
        response = self.client.post(self.checkout_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(OrderModel.objects.count(), initial_order_count)

        self.mock_validate_quantity_in_cart_summer_class.assert_not_called()
        self.mock_zarinpal_class.assert_not_called()

    def test_context_data(self):
        response = self.client.get(self.checkout_url)
        self.assertIn("addresses", response.context)
        self.assertEqual(list(response.context["addresses"]), [self.address])

        total_price = self.cart.calculate_total_price()
        self.assertIn("total_price", response.context)
        self.assertEqual(response.context["total_price"], total_price)
        self.assertIn("total_tax", response.context)
        self.assertEqual(
            response.context["total_tax"], round((total_price * 9) / 100)
        )


class OrderCompletedViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
        )
        cls.url = reverse("order:completed")

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class OrderFailedViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
        )
        cls.url = reverse("order:failed")

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class OrderValidateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
        )

        cls.url = reverse("order:validate-coupon")

    def test_anonymous_user(self):
        data = {"code": "MyCode"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

    @patch("order.views.CouponModel.objects")
    def test_coupon_do_not_exists(self, mock_coupon_manager):
        self.client.force_login(self.user)
        mock_coupon_manager.get.side_effect = CouponModel.DoesNotExist
        data = {"code": "InvalidCode"}
        response = self.client.post(self.url, data)
        response = response.json()
        self.assertEqual(response["message"], "کد تخفیف یافت نشد")

    @patch("order.views.CouponModel.objects")
    def test_coupon_usage_limit_exceeded(self, mock_coupon_manager):
        self.client.force_login(self.user)
        mock_coupon = MagicMock()
        mock_coupon.used_by.count.return_value = 4
        mock_coupon.max_limit_usage = 4

        mock_coupon_manager.get.return_value = mock_coupon

        data = {"code": "InvalidCode"}
        response = self.client.post(self.url, data)
        response = response.json()
        self.assertEqual(response["message"], "محدودیت در تعداد استفاده")
        mock_coupon_manager.get.assert_called_once_with(code="InvalidCode")

    @patch("order.views.CouponModel.objects")
    def test_coupon_expired(self, mock_coupon_manager):
        self.client.force_login(self.user)
        mock_coupon = MagicMock()
        mock_coupon.used_by.count.return_value = 2
        mock_coupon.max_limit_usage = 4
        mock_coupon.expiration_date = timezone.now() - datetime.timedelta(
            days=1
        )
        mock_coupon_manager.get.return_value = mock_coupon

        data = {"code": "ExpiredCode"}
        response = self.client.post(self.url, data)
        response = response.json()
        self.assertEqual(response["message"], "کد تخفیف منقضی شده است")
        mock_coupon_manager.get.assert_called_once_with(code="ExpiredCode")

    @patch("order.views.CouponModel.objects")
    def test_coupon_used(self, mock_coupon_manager):
        self.client.force_login(self.user)
        mock_coupon = MagicMock()
        mock_coupon.used_by.count.return_value = 2
        mock_coupon.max_limit_usage = 4
        mock_coupon.expiration_date = timezone.now() + datetime.timedelta(
            days=2
        )
        mock_coupon.used_by.all.return_value = [
            self.user,
        ]
        mock_coupon_manager.get.return_value = mock_coupon

        data = {"code": "CodeUsed"}
        response = self.client.post(self.url, data)
        response = response.json()
        self.assertEqual(
            response["message"], "این کد تخفیف قبلا توسط شما استفاده شده است"
        )
        mock_coupon_manager.get.assert_called_once_with(code="CodeUsed")

    @patch("order.views.CouponModel.objects")
    def test_valid_coupon_success(self, mock_coupon_manager):
        cart = CartModel.objects.create(user=self.user)
        category = ProductCategoryModel.objects.create(
            title="Category test", slug="category-test"
        )
        product = ProductModel.objects.create(
            user=self.user,
            category=category,
            title="Product test",
            slug="product-test",
            description="This is description",
            stock=15,
            price=100,
            status=ProductStatusType.publish.value,
        )
        cart_item = CartItemModel.objects.create(
            cart=cart, product=product, quantity=10
        )

        self.client.force_login(self.user)

        mock_coupon = MagicMock()
        mock_coupon.used_by.count.return_value = 2
        mock_coupon.max_limit_usage = 4
        mock_coupon.expiration_date = timezone.now() + datetime.timedelta(
            days=2
        )
        mock_coupon.discount_percent = 20

        mock_coupon_manager.get.return_value = mock_coupon

        data = {"code": "ValidCode"}
        response = self.client.post(self.url, data)

        response = response.json()
        self.assertEqual(response["message"], "کد تخفیف با موفقیت ثبت شد")
        mock_coupon_manager.get.assert_called_once_with(code="ValidCode")

        self.assertEqual(response["total_price"], 800)
        self.assertEqual(response["total_tax"], 72)
