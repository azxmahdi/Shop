from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import UserType
from dashboard.admin.forms import ReviewForm
from review.models import ReviewModel, ReviewStatusType
from shop.models import ProductCategoryModel, ProductModel, ProductStatusType

User = get_user_model()


class AdminReviewFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            email="test@example.com",
            password="Test123/",
            type=UserType.admin.value,
        )

        cls.category = ProductCategoryModel.objects.create(
            title="test category", slug="test-category"
        )
        cls.product = ProductModel.objects.create(
            user=cls.admin,
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
            user=cls.admin,
            product=cls.product,
            description="This is a test description",
            rate=4,
            status=ReviewStatusType.pending.value,
        )

        cls.valid_data = {
            "description": "This is a test description",
            "rate": 4,
            "status": ReviewStatusType.pending.value,
        }

    def test_review_form_with_valid_data(self):
        form = ReviewForm(instance=self.review, data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_clean_method_prevents_immutable_field_changes(self):
        invalid_data = self.valid_data.copy()
        invalid_data["description"] = "This is a test description updated"

        form = ReviewForm(instance=self.review, data=invalid_data)

        self.assertFalse(form.is_valid())

        self.assertIn("description", form.errors)
        self.assertEqual(
            form.errors["description"][0],
            f"تغییر این فیلد مجاز نیست. مقدار فعلی: {self.review.description}",
        )

        invalid_data = self.valid_data.copy()
        invalid_data["rate"] = 1

        form = ReviewForm(instance=self.review, data=invalid_data)

        self.assertIn("rate", form.errors)
        self.assertEqual(
            form.errors["rate"][0],
            f"تغییر این فیلد مجاز نیست. مقدار فعلی: {self.review.rate}",
        )
