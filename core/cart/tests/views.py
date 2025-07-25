import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from shop.models import ProductCategoryModel, ProductModel, ProductStatusType

User = get_user_model()


class SessionAddProductViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test_create_product@example.com", password="Test123@"
        )
        self.category = ProductCategoryModel.objects.create(
            title="Category test", slug="category-test"
        )
        self.product = ProductModel.objects.create(
            user=self.user,
            category=self.category,
            title="Product test",
            slug="product-test",
            description="This is description",
            stock=10,
            discount_percent=20,
            price=100,
            status=ProductStatusType.publish.value,
        )
        self.product_id = self.product.id
        self.url = reverse("cart:session-add-product")

    def test_add_product_unauthenticated(self):
        response = self.client.post(self.url, {"product_id": self.product_id})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["total_quantity"], 1)
        self.assertEqual(
            data["cart"]["items"][str(self.product_id)]["quantity"], 1
        )

    def test_add_product_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {"product_id": self.product_id})
        self.assertEqual(response.status_code, 200)
        from cart.models import CartItemModel

        self.assertTrue(
            CartItemModel.objects.filter(product=self.product).exists()
        )


class SessionRemoveProductViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test_create_product@example.com", password="Test123@"
        )
        self.category = ProductCategoryModel.objects.create(
            title="Category test", slug="category-test"
        )
        self.product = ProductModel.objects.create(
            user=self.user,
            category=self.category,
            title="Product test",
            slug="product-test",
            description="This is description",
            stock=10,
            discount_percent=20,
            price=100,
            status=ProductStatusType.publish.value,
        )
        self.product_id = self.product.id
        self.url = reverse("cart:session-remove-product")
        self.client.post(
            reverse("cart:session-add-product"),
            {"product_id": self.product_id},
        )

    def test_remove_product(self):
        response = self.client.post(self.url, {"product_id": self.product_id})
        data = json.loads(response.content)
        self.assertEqual(data["total_quantity"], 0)
        self.assertNotIn(str(self.product_id), data["cart"]["items"])


class SessionUpdateProductQuantityViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test_create_product@example.com", password="Test123@"
        )
        self.category = ProductCategoryModel.objects.create(
            title="Category test", slug="category-test"
        )
        self.product = ProductModel.objects.create(
            user=self.user,
            category=self.category,
            title="Product test",
            slug="product-test",
            description="This is description",
            stock=10,
            discount_percent=20,
            price=100,
            status=ProductStatusType.publish.value,
        )
        self.url = reverse("cart:session-update-product-quantity")
        self.product_id = self.product.id
        self.client.post(
            reverse("cart:session-add-product"),
            {"product_id": self.product_id},
        )

    def test_update_quantity(self):
        response = self.client.post(
            self.url, {"product_id": self.product_id, "quantity": 5}
        )
        data = json.loads(response.content)
        self.assertEqual(data["total_quantity"], 5)


class CartSummaryViewTest(TestCase):
    def test_cart_summary_context(self):
        user = User.objects.create_user(
            email="test_create_product@example.com", password="Test123@"
        )
        category = ProductCategoryModel.objects.create(
            title="Category test", slug="category-test"
        )
        product = ProductModel.objects.create(
            user=user,
            category=category,
            title="Product test",
            slug="product-test",
            description="This is description",
            stock=10,
            price=100,
            status=ProductStatusType.publish.value,
        )
        self.client.post(
            reverse("cart:session-add-product"), {"product_id": product.id}
        )
        response = self.client.get(reverse("cart:cart-summary"))
        self.assertContains(response, "Product test")
        self.assertEqual(response.context["total_quantity"], 1)
        self.assertEqual(response.context["total_payment_price"], 100)


class CheckIsProductViewTest(TestCase):
    def test_product_in_cart(self):
        user = User.objects.create_user(
            email="test_create_product@example.com", password="Test123@"
        )
        category = ProductCategoryModel.objects.create(
            title="Category test", slug="category-test"
        )
        product = ProductModel.objects.create(
            user=user,
            category=category,
            title="Product test",
            slug="product-test",
            description="This is description",
            stock=10,
            discount_percent=20,
            price=100,
            status=ProductStatusType.publish.value,
        )
        self.client.post(
            reverse("cart:session-add-product"), {"product_id": product.id}
        )
        response = self.client.post(
            reverse("cart:session-check-is-product"),
            {"product_id": product.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = json.loads(response.content)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["total_payment_product"], 80)

    def test_product_not_in_cart(self):
        response = self.client.post(
            reverse("cart:session-check-is-product"),
            {"product_id": 999},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(json.loads(response.content)["status"], "no")


class SessionUpdateProductQuantityDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test_create_product@example.com", password="Test123@"
        )
        self.category = ProductCategoryModel.objects.create(
            title="Category test", slug="category-test"
        )
        self.product = ProductModel.objects.create(
            user=self.user,
            category=self.category,
            title="Product test",
            slug="product-test",
            description="This is description",
            stock=3,
            discount_percent=20,
            price=100,
            status=ProductStatusType.publish.value,
        )
        self.url = reverse("cart:session-update-product-quantity-detail")
        self.product_id = self.product.id
        self.client.post(
            reverse("cart:session-add-product"),
            {"product_id": self.product_id},
        )

    def test_update_quantity_exceeds_stock(self):
        response = self.client.post(
            self.url,
            {"product_id": self.product_id, "quantity": 5},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = json.loads(response.content)
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["selected_quantity"], 1)

    def test_update_quantity_negative(self):
        response = self.client.post(
            self.url,
            {"product_id": self.product_id, "quantity": -1},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = json.loads(response.content)
        self.assertEqual(data["status"], "error")
