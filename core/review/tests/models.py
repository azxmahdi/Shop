from django.contrib.auth import get_user_model
from django.test import TestCase

from shop.models import ProductCategoryModel, ProductModel, ProductStatusType

from ..models import ReviewModel, ReviewStatusType

User = get_user_model()


class TestReviewStatusType(TestCase):
    def test_choices_structure(self):
        expected_choices = [
            (1, "در انتظار تایید"),
            (2, "تایید شده"),
            (3, "رد شده"),
        ]
        self.assertEqual(expected_choices, ReviewStatusType.choices)


class TestReview(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="testuser@example.com",
            password="test123",
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
        cls.review = ReviewModel.objects.create(
            user=cls.user,
            product=cls.product,
            description="This is a test review",
            rate=5,
            status=ReviewStatusType.accepted.value,
        )

    def test_review_creation(self):
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.product, self.product)
        self.assertEqual(self.review.description, "This is a test review")
        self.assertEqual(self.review.rate, 5)
        self.assertEqual(self.review.status, ReviewStatusType.accepted.value)

    def test_get_status_func(self):
        self.assertEqual(self.review.get_status()["id"], 2)
        self.assertEqual(
            self.review.get_status()["title"], ReviewStatusType.accepted.name
        )
        self.assertEqual(self.review.get_status()["label"], "تایید شده")

    def test_avg_rate_updated_on_review_acceptance(self):
        self.review

        review2 = ReviewModel.objects.create(
            user=self.user,
            product=self.product,
            description="This is a test review",
            rate=4,
            status=ReviewStatusType.accepted.value,
        )

        self.assertEqual(self.product.avg_rate, 4.5)
