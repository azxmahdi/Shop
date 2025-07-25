from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserType
from review.models import ReviewModel, ReviewStatusType
from shop.models import ProductCategoryModel, ProductModel, ProductStatusType

User = get_user_model()


class AdminReviewListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="test@example.com", password="Test123/"
        )
        cls.admin = User.objects.create_user(
            email="admin@example.com",
            password="Admin123/",
            type=UserType.admin.value,
        )

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
        cls.review = ReviewModel.objects.create(
            user=cls.user,
            product=cls.product,
            description="This is description review",
            rate=5,
        )

        cls.url = reverse("dashboard:admin:review-list")

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_admin_user(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, self.review.user.user_profile.get_fullname()
        )

    def test_context_data(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)

        self.assertEqual(
            response.context["total_items"], ReviewModel.objects.count()
        )
        self.assertEqual(
            response.context["status_types"],
            ReviewStatusType.choices,
        )


class AdminReviewEditViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="test@example.com", password="Test123/"
        )
        cls.admin = User.objects.create_user(
            email="admin@example.com",
            password="Admin123/",
            type=UserType.admin.value,
        )

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
        cls.review = ReviewModel.objects.create(
            user=cls.user,
            product=cls.product,
            description="This is description review",
            rate=3,
        )

        cls.url = reverse(
            "dashboard:admin:review-edit", kwargs={"pk": cls.review.pk}
        )

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_admin_user(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.review.description)

    def test_review_edit_with_valid_data(self):
        self.client.force_login(self.admin)
        data = {
            "rate": self.review.rate,
            "description": self.review.description,
            "status": ReviewStatusType.accepted.value,
        }

        response = self.client.post(self.url, data, follow=True)
        self.assertContains(response, "تغییرات با موفقیت اعمال شد")

        self.review.refresh_from_db()
        self.assertEqual(self.review.status, ReviewStatusType.accepted.value)

    def test_review_edit_with_invalid_data(self):
        self.client.force_login(self.admin)
        data = {
            "rate": 5,
            "description": "This is description review updated",
            "status": ReviewStatusType.accepted.value,
        }

        response = self.client.post(self.url, data, follow=True)
        self.assertNotContains(response, "تغییرات با موفقیت اعمال شد")
        self.review.refresh_from_db()
        self.assertNotEqual(
            self.review.description, "This is description review updated"
        )
        self.assertNotEqual(self.review.rate, 5)
