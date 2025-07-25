from django.contrib.auth import get_user_model
from django.test import TestCase

from review.forms import SubmitReviewForm
from review.models import ReviewModel, ReviewStatusType
from shop.models import ProductCategoryModel, ProductModel, ProductStatusType

User = get_user_model()


class SubmitReviewFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com",
            password="User123/",
        )
        cls.category = ProductCategoryModel.objects.create(
            title="Category test", slug="category-test"
        )
        cls.product = ProductModel.objects.create(
            user=cls.user,
            category=cls.category,
            title="Product test",
            slug="product-test",
            description="This is a description",
            stock=10,
            discount_percent=20,
            price=100,
            status=ProductStatusType.publish.value,
        )

        cls.unpublished_product = ProductModel.objects.create(
            user=cls.user,
            category=cls.category,
            title="Unpublished Product",
            slug="unpublished-product",
            description="This is an unpublished product",
            stock=5,
            discount_percent=10,
            price=50,
            status=ProductStatusType.draft.value,
        )

        cls.instance = ReviewModel.objects.create(
            user=cls.user,
            product=cls.product,
            description="This is a description",
            rate=4,
            status=ReviewStatusType.pending.value,
        )
        cls.valid_data = {
            "product": cls.product.pk,
            "rate": 4,
            "description": "This is a description",
        }

    def test_form_for_product_does_not_exists(self):

        invalid_data = self.valid_data.copy()
        invalid_data["product"] = self.unpublished_product.pk

        form = SubmitReviewForm(data=invalid_data, instance=self.instance)
        self.assertFalse(form.is_valid())
        self.assertIn("این محصول وجود ندارد", form.errors["__all__"])

    def test_form_with_invalid_data(self):
        invalid_data = self.valid_data.copy()
        invalid_data["description"] = ""
        form = SubmitReviewForm(data=invalid_data, instance=self.instance)
        self.assertFalse(form.is_valid())
        self.assertIn("فیلد توضیحات اجباری است", form.errors["description"])
