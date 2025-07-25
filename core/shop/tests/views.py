from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import UserType
from review.models import ReviewModel, ReviewStatusType
from shop.models import (
    ProductCategoryModel,
    ProductModel,
    ProductStatusType,
    WishlistProductModel,
)

User = get_user_model()


class ShopProductGridViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("shop:product-grid")

        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="Admin123/",
            type=UserType.admin.value,
        )

        self.parent_category = ProductCategoryModel.objects.create(
            title="Parent Category", slug="parent-category"
        )

        self.category1 = ProductCategoryModel.objects.create(
            title="Category test 1",
            slug="category-test-1",
            parent=self.parent_category,
        )

        self.category2 = ProductCategoryModel.objects.create(
            title="Category test 2",
            slug="category-test-2",
            parent=self.parent_category,
        )

        self.product1 = ProductModel.objects.create(
            user=self.admin,
            category=self.category1,
            title="First",
            slug="first",
            description="This is description",
            stock=10,
            discount_percent=0,
            price=50,
            status=ProductStatusType.publish.value,
        )
        self.product2 = ProductModel.objects.create(
            user=self.admin,
            category=self.category1,
            title="Middle",
            slug="middle",
            description="This is description",
            stock=6,
            discount_percent=35,
            price=150,
            status=ProductStatusType.publish.value,
        )
        self.product3 = ProductModel.objects.create(
            user=self.admin,
            category=self.category2,
            title="Last",
            slug="last",
            description="This is description",
            stock=12,
            discount_percent=10,
            price=300,
            status=ProductStatusType.publish.value,
        )
        self.product4 = ProductModel.objects.create(
            user=self.admin,
            category=self.parent_category,
            title="Parent Product",
            slug="parent-product",
            description="This is description",
            stock=5,
            price=200,
            status=ProductStatusType.publish.value,
        )

    def test_view_url_accessible(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_context_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["total_items"], 4)
        self.assertIn(self.parent_category, response.context["categories"])
        self.assertEqual(response.context["current_filters"].dict(), {})
        self.assertEqual(response.context["features"], [])

    def test_queryset_filters_by_category_search_and_price_and_order_by(self):
        resp_parent = self.client.get(
            f"{self.url}?category_id={self.parent_category.id}"
        )
        self.assertEqual(len(resp_parent.context["object_list"]), 4)

        resp_cat1 = self.client.get(
            f"{self.url}?category_id={self.category1.id}"
        )
        self.assertEqual(len(resp_cat1.context["object_list"]), 2)

        resp_q = self.client.get(f"{self.url}?q=Middle")
        self.assertEqual(len(resp_q.context["object_list"]), 1)
        self.assertEqual(resp_q.context["object_list"][0], self.product2)

        resp_price = self.client.get(f"{self.url}?min_price=100&max_price=200")
        self.assertCountEqual(
            resp_price.context["object_list"], [self.product2, self.product4]
        )

        resp_order = self.client.get(f"{self.url}?order_by=-price")
        prices = [p.price for p in resp_order.context["object_list"]]
        self.assertEqual(prices, [300, 200, 150, 50])

    def test_page_size_via_queryparam(self):
        resp = self.client.get(f"{self.url}?page_size=2")
        self.assertEqual(len(resp.context["object_list"]), 2)
        self.assertEqual(resp.context["total_items"], 4)

    def test_price_filter(self):
        response = self.client.get(f"{self.url}?min_price=50&max_price=100")
        self.assertEqual(len(response.context["object_list"]), 1)
        self.assertEqual(response.context["object_list"][0].title, "First")


class ShopProductDetailViewTest(TestCase):
    def setUp(self):

        self.client = Client()

        self.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
        )

        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="Admin123/",
            type=UserType.admin.value,
        )
        self.category = ProductCategoryModel.objects.create(
            title="Test Category", slug="test-category"
        )
        self.product = ProductModel.objects.create(
            user=self.admin,
            category=self.category,
            title="Product test",
            slug="product-test",
            description="This is description",
            stock=10,
            discount_percent=0,
            price=50,
            status=ProductStatusType.publish.value,
        )
        self.url = reverse(
            "shop:product-detail", kwargs={"slug": self.product.slug}
        )

        self.review1 = ReviewModel.objects.create(
            product=self.product,
            user=self.user,
            description="This is review1 description",
            rate=5,
            status=ReviewStatusType.accepted.value,
        )
        self.review2 = ReviewModel.objects.create(
            product=self.product,
            user=self.user,
            description="This is review2 description",
            rate=3,
            status=ReviewStatusType.accepted.value,
        )

    def test_view_url_accessible(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_product_details(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["product"], self.product)
        self.assertContains(response, self.product.title)
        self.assertContains(response, self.product.price)

    def test_review_data_in_context(self):
        response = self.client.get(self.url)
        reviews = response.context["reviews"]
        self.assertEqual(reviews.count(), 2)
        self.assertIn(self.review1, reviews)
        self.assertIn(self.review2, reviews)

        star_counts = response.context["star_counts"]
        self.assertEqual(star_counts[0], (5, 1, 50))
        self.assertEqual(star_counts[2], (3, 1, 50))

        self.assertEqual(response.context["recommend_percentage"], 50)


class AddOrRemoveWishlistViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
        )

        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="Admin123/",
            type=UserType.admin.value,
        )
        self.category = ProductCategoryModel.objects.create(
            title="Test Category", slug="test-category"
        )
        self.product = ProductModel.objects.create(
            user=self.admin,
            category=self.category,
            title="Product test",
            slug="product-test",
            description="This is description",
            stock=10,
            discount_percent=0,
            price=50,
            status=ProductStatusType.publish.value,
        )
        self.url = reverse("shop:add-or-remove-wishlist")

    def test_add_to_wishlist_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {"product_id": self.product.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["message"], "محصول به لیست علایق اضافه شد"
        )
        self.assertTrue(
            WishlistProductModel.objects.filter(
                user=self.user, product=self.product
            ).exists()
        )

    def test_remove_from_wishlist_authenticated(self):
        WishlistProductModel.objects.create(
            user=self.user, product=self.product
        )

        self.client.force_login(self.user)
        response = self.client.post(self.url, {"product_id": self.product.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["message"], "محصول از لیست علایق حذف شد"
        )
        self.assertFalse(
            WishlistProductModel.objects.filter(
                user=self.user, product=self.product
            ).exists()
        )

    def test_unauthenticated_access(self):
        response = self.client.post(self.url, {"product_id": self.product.id})
        self.assertEqual(response.status_code, 302)


class CategoriesSidebarViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("shop:categories-sidebar")

        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="Admin123/",
            type=UserType.admin.value,
        )
        self.parent_category = ProductCategoryModel.objects.create(
            title="Parent Category", slug="parent-category"
        )
        self.child_category = ProductCategoryModel.objects.create(
            title="Child Category",
            slug="child-category",
            parent=self.parent_category,
        )

        self.mobile_category = ProductCategoryModel.objects.create(
            title="Mobile Phones", slug="mobile-phones"
        )
        self.mens_category = ProductCategoryModel.objects.create(
            title="Mens Clothing", slug="mens-clothing"
        )

        self.mobile_product = ProductModel.objects.create(
            user=self.admin,
            category=self.mobile_category,
            title="Mobile Phone",
            slug="mobile-phone",
            description="This is description",
            stock=10,
            discount_percent=0,
            price=50,
            status=ProductStatusType.publish.value,
        )

        self.mens_product = ProductModel.objects.create(
            user=self.admin,
            category=self.mens_category,
            title="Shirt",
            slug="shirt",
            description="This is description",
            stock=10,
            discount_percent=0,
            price=50,
            status=ProductStatusType.publish.value,
        )

        self.popular_product1 = ProductModel.objects.create(
            user=self.admin,
            category=self.child_category,
            title="Popular Product 1",
            slug="popular-product-1",
            description="This is description",
            stock=10,
            discount_percent=0,
            price=50,
            status=ProductStatusType.publish.value,
        )
        self.popular_product2 = ProductModel.objects.create(
            user=self.admin,
            category=self.child_category,
            title="Popular Product 2",
            slug="popular-product-2",
            description="This is description",
            stock=10,
            discount_percent=0,
            price=50,
            status=ProductStatusType.publish.value,
        )
        self.popular_product3 = ProductModel.objects.create(
            user=self.admin,
            category=self.child_category,
            title="Popular Product 3",
            slug="popular-product-3",
            description="This is description",
            stock=10,
            discount_percent=0,
            price=50,
            status=ProductStatusType.publish.value,
        )

    def test_view_url_accessible(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_min_prices_in_context(self):
        response = self.client.get(self.url)

        min_price_mobile = response.context.get("min_price_mobile_phones")
        self.assertIsNotNone(min_price_mobile)
        self.assertEqual(min_price_mobile["min_price"], 50)

        min_price_mens = response.context.get("min_price_mens_clothing")
        self.assertIsNotNone(min_price_mens)
        self.assertEqual(min_price_mens["min_price"], 50)

    def test_popular_products(self):
        response = self.client.get(self.url)
        popular_products = response.context["poplar_products"]

        self.assertEqual(len(popular_products), 3)

        created_dates = [p.created_date for p in popular_products]
        self.assertEqual(created_dates, sorted(created_dates, reverse=True))
