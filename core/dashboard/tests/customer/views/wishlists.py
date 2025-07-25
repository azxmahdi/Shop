from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from shop.models import (
    ProductCategoryModel,
    ProductModel,
    ProductStatusType,
    WishlistProductModel,
)

User = get_user_model()


class CustomerWishListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
        )
        cls.category = ProductCategoryModel.objects.create(
            title="Category test", slug="category-test"
        )
        cls.product1 = ProductModel.objects.create(
            user=cls.user,
            category=cls.category,
            title="laptopA",
            slug="laptop-a",
            description="This is description 1",
            stock=10,
            discount_percent=20,
            price=100,
            status=ProductStatusType.publish.value,
        )
        cls.product2 = ProductModel.objects.create(
            user=cls.user,
            category=cls.category,
            title="mobileB",
            slug="laptop-b",
            description="This is description 2",
            stock=10,
            discount_percent=20,
            price=100,
            status=ProductStatusType.publish.value,
        )
        cls.wishlist1 = WishlistProductModel.objects.create(
            user=cls.user, product=cls.product1
        )
        cls.wishlist2 = WishlistProductModel.objects.create(
            user=cls.user, product=cls.product2
        )
        cls.url = reverse("dashboard:customer:wishlist-list")

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.wishlist1.product.title)

    def test_search_functionality(self):
        self.client.force_login(self.user)
        url = self.url + f"?q={self.wishlist1.product.title}"
        response = self.client.get(url)
        self.assertContains(response, self.wishlist1.product.title)
        self.assertNotContains(response, self.wishlist2.product.title)

    def test_context_data(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(
            response.context["total_items"],
            WishlistProductModel.objects.all().count(),
        )


class CustomerWishListDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
        )
        cls.category = ProductCategoryModel.objects.create(
            title="Category test", slug="category-test"
        )

        cls.product = ProductModel.objects.create(
            user=cls.user,
            category=cls.category,
            title="Product Test",
            slug="product-Test",
            description="This is description",
            stock=10,
            discount_percent=20,
            price=100,
            status=ProductStatusType.publish.value,
        )
        cls.wishlist = WishlistProductModel.objects.create(
            user=cls.user, product=cls.product
        )

        cls.url = reverse(
            "dashboard:customer:wishlist-delete",
            kwargs={"pk": cls.wishlist.pk},
        )

    def test_anonymous_user(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, follow=True)
        self.assertContains(response, "محصول با موفقیت از لیست حذف شد")
        self.assertFalse(
            WishlistProductModel.objects.filter(user=self.user).exists()
        )
