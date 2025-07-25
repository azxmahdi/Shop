from django.contrib.auth import get_user_model
from django.test import TestCase

from shop.models import ProductCategoryModel, ProductModel, ProductStatusType

from ..models import CartItemModel, CartModel

User = get_user_model()


class TestCart(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="testuser@example.com",
            password="test123",
        )

    def test_cart_creation(self):
        cart = CartModel.objects.create(user=self.user)
        self.assertEqual(cart.user, self.user)


class TestCartItem(TestCart):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="testuser@example.com",
            password="test123",
        )
        cls.cart = CartModel.objects.create(user=cls.user)
        cls.category = ProductCategoryModel.objects.create(
            title="Category test", slug="category-test"
        )
        cls.product = ProductModel.objects.create(
            user=cls.user,
            category=cls.category,
            title="Product test",
            slug="product-test",
            description="This is description",
            stock=10,
            discount_percent=20,
            price=100,
            status=ProductStatusType.publish.value,
        )

    def test_cart_item_creation(self):

        cart_item = CartItemModel.objects.create(
            cart=self.cart, product=self.product, quantity=2
        )
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 2)
