from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import RequestFactory, TestCase
from django.urls import reverse

from shop.models import ProductCategoryModel, ProductModel, ProductStatusType

User = get_user_model()


class SubmitReviewViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
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
        cls.data = {
            "product": cls.product.pk,
            "rate": 4,
            "description": "This is a review description",
        }
        cls.url = reverse("review:submit-review")

    def test_anonymous_user(self):
        response = self.client.post(path=self.url, data=self.data)
        self.assertEqual(response.status_code, 302)

    def test_submit_review_with_valid_data(self):
        self.client.force_login(self.user)
        response = self.client.post(path=self.url, data=self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "دیدگاه شما با موفقیت ثبت شد و پس از بررسی نمایش داده خواهد شد",
        )

    def test_submit_review_with_valid_data(self):
        self.client.force_login(self.user)
        response = self.client.post(path=self.url, data=self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "دیدگاه شما با موفقیت ثبت شد و پس از بررسی نمایش داده خواهد شد",
        )

    def test_submit_review_with_invalid_data(self):
        invalid_data = self.data.copy()
        invalid_data["description"] = ""
        self.client.force_login(self.user)

        response = self.client.post(
            path=self.url,
            data=invalid_data,
            follow=True,
            HTTP_REFERER=reverse(
                "shop:product-detail", kwargs={"slug": self.product.slug}
            ),
        )

        self.assertRedirects(
            response,
            reverse("shop:product-detail", kwargs={"slug": self.product.slug}),
        )

        messages = list(get_messages(response.wsgi_request))

        self.assertTrue(len(messages) > 0)
        self.assertEqual(messages[0].tags, "error")
        self.assertEqual(str(messages[0]), "فیلد توضیحات اجباری است")
