from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import UserType
from payment.models import PaymentModel, PaymentStatusType
from shop.models import ProductCategoryModel, ProductModel, ProductStatusType

from ..models import (
    CouponModel,
    OrderItemModel,
    OrderModel,
    OrderStatusType,
    UserAddressModel,
)

User = get_user_model()


class TestOrderStatusType(TestCase):
    def test_choices_structure(self):
        expected_choices = [
            (1, "در انتظار پرداخت"),
            (2, "موفقیت آمیز"),
            (3, "لغو شده"),
        ]
        self.assertEqual(expected_choices, OrderStatusType.choices)


class TestUserAddress(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="testuser@example.com",
            password="test123",
        )

    def test_user_address_creation(self):
        address = UserAddressModel.objects.create(
            user=self.user,
            address="test address",
            state="test state",
            city="test city",
            zip_code="12345",
        )
        self.assertEqual(address.user, self.user)
        self.assertEqual(address.address, "test address")
        self.assertEqual(address.state, "test state")
        self.assertEqual(address.city, "test city")
        self.assertEqual(address.zip_code, "12345")


class TestOrder(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="testuser@example.com",
            password="test123",
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
            payment=cls.payment,
            coupon=None,
            status=OrderStatusType.pending.value,
        )
        cls.category = ProductCategoryModel.objects.create(
            title="Category test", slug="category-test"
        )
        cls.product = ProductModel.objects.create(
            user=cls.user,
            category=cls.category,
            title="Product test ",
            slug="product-test",
            description="This is description",
            stock=4,
            discount_percent=10,
            price=500,
            status=ProductStatusType.publish.value,
        )
        cls.order_item = OrderItemModel.objects.create(
            order=cls.order,
            product=cls.product,
            quantity=2,
            price=cls.product.get_price(),
        )
        cls.order.total_price = cls.order.calculate_total_price()

    def test_order_creation(self):
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.address, "test address")
        self.assertEqual(self.order.state, "test state")
        self.assertEqual(self.order.city, "test city")
        self.assertEqual(self.order.zip_code, "12345")
        self.assertEqual(self.order.payment, self.payment)
        self.assertIsNone(self.order.coupon)
        self.assertEqual(self.order.status, OrderStatusType.pending.value)

    def test_calculate_total_price_func(self):
        expected_price = 900
        self.assertEqual(self.order.calculate_total_price(), expected_price)

    def test_get_status_func(self):
        self.assertEqual(self.order.get_status()["id"], 1)
        self.assertEqual(self.order.get_status()["title"], "pending")
        self.assertEqual(self.order.get_status()["label"], "در انتظار پرداخت")

    def test_get_full_address_func(self):
        self.assertEqual(
            self.order.get_full_address(), "test state,test city,test address"
        )

    def test_is_successful_func(self):
        self.assertFalse(self.order.is_successful)

    def test_get_price_func(self):
        self.order.coupon = CouponModel.objects.create(
            user=self.admin,
            code="TEST_COUPON",
            discount_percent=20,
            max_limit_usage=10,
        )
        self.order.total_price = self.order.calculate_total_price()
        expected_price = 900 - (900 * 20 / 100)
        self.assertEqual(self.order.get_price(), expected_price)


class TestOrderItem(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="testuser@example.com",
            password="test123",
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
            payment=cls.payment,
            coupon=None,
            status=OrderStatusType.pending.value,
        )
        cls.category = ProductCategoryModel.objects.create(
            title="Category test", slug="category-test"
        )
        cls.product = ProductModel.objects.create(
            user=cls.user,
            category=cls.category,
            title="Product test ",
            slug="product-test",
            description="This is description",
            stock=4,
            discount_percent=10,
            price=500,
            status=ProductStatusType.publish.value,
        )
        cls.order_item = OrderItemModel.objects.create(
            order=cls.order,
            product=cls.product,
            quantity=2,
            price=cls.product.get_price(),
        )

    def test_order_item_creation(self):
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.price, self.product.get_price())


class TestCoupon(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            email="admin@example.com",
            password="Admin123/",
            type=UserType.admin.value,
        )
        cls.coupon = CouponModel.objects.create(
            user=cls.admin,
            code="TEST_COUPON",
            discount_percent=20,
            max_limit_usage=10,
        )

    def test_coupon_creation(self):
        self.assertEqual(self.coupon.code, "TEST_COUPON")
        self.assertEqual(self.coupon.discount_percent, 20)
        self.assertEqual(self.coupon.max_limit_usage, 10)
