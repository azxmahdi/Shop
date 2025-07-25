from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from accounts.models import UserType
from dashboard.admin.forms import ProductImageForm
from shop.models import (
    CategoryFeature,
    FeatureOption,
    ProductCategoryModel,
    ProductFeature,
    ProductModel,
    ProductStatusType,
)

User = get_user_model()


class AdminProductListViewTest(TestCase):
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

        cls.product1 = ProductModel.objects.create(
            user=cls.user,
            category=cls.category,
            title="Product test 1",
            slug="product-test-1",
            description="This is description",
            stock=10,
            discount_percent=20,
            price=100,
            status=ProductStatusType.publish.value,
        )
        cls.product2 = ProductModel.objects.create(
            user=cls.user,
            category=cls.category,
            title="Product test 2",
            slug="product-test-2",
            description="This is description",
            stock=6,
            discount_percent=5,
            price=12,
            status=ProductStatusType.publish.value,
        )

        cls.url = reverse("dashboard:admin:product-list")

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
        self.assertContains(response, self.product1.title)

    def test_search_functionality(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url + "?q=Product test 1")

        self.assertContains(response, self.product1.title)
        self.assertNotContains(response, self.product2.title)

    def test_context_data(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)

        self.assertEqual(
            response.context["total_items"], ProductModel.objects.count()
        )

        self.assertQuerysetEqual(
            response.context["categories"],
            ProductCategoryModel.objects.all(),
            ordered=False,
        )


class AdminProductCreateViewTest(TestCase):
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

        cls.parent_category = ProductCategoryModel.objects.create(
            title="Parent Category", slug="parent-category"
        )
        cls.category = ProductCategoryModel.objects.create(
            title="Category Test",
            slug="category-test",
            parent=cls.parent_category,
        )
        cls.url = reverse("dashboard:admin:product-create")

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

    def test_product_creation_with_valid_data(self):
        self.client.force_login(self.admin)

        form_data = {
            "title": "New Product",
            "slug": "new-product",
            "category": self.category.id,
            "price": 100,
            "status": ProductStatusType.publish.value,
            "brief_description": "Test brief",
            "description": "Test description",
            "stock": 10,
            "discount_percent": 0,
        }

        self.client.post(
            self.url,
            data=form_data,
        )

        self.assertEqual(ProductModel.objects.count(), 1)
        product = ProductModel.objects.get(slug="new-product")
        self.assertEqual(product.status, ProductStatusType.not_completed.value)

    def test_redirect_after_creation(self):
        self.client.force_login(self.admin)

        form_data = {
            "title": "New Product",
            "slug": "new-product",
            "category": self.category.id,
            "price": 100,
            "status": ProductStatusType.publish.value,
            "brief_description": "Test brief",
            "description": "Test description",
            "stock": 10,
            "discount_percent": 0,
        }

        response = self.client.post(self.url, form_data)
        new_product = ProductModel.objects.get(slug="new-product")

        expected_url = reverse_lazy(
            "dashboard:admin:add-product-feature",
            kwargs={
                "product_id": new_product.pk,
                "status": form_data["status"],
            },
        )
        self.assertRedirects(response, expected_url)

    def test_invalid_form_submission(self):
        self.client.force_login(self.admin)

        invalid_data = {
            "slug": "new-product",
            "description": "This is a description",
            "category": self.category.pk,
            "price": 100,
            "status": ProductStatusType.publish.value,
        }

        response = self.client.post(self.url, invalid_data)

        self.assertEqual(ProductModel.objects.count(), 0)

        self.assertFormError(
            response, "form", "title", "This field is required."
        )


class AdminProductEditViewTest(TestCase):
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

        cls.parent_category = ProductCategoryModel.objects.create(
            title="Parent Category", slug="parent-category"
        )
        cls.category = ProductCategoryModel.objects.create(
            title="Category Test",
            slug="category-test",
            parent=cls.parent_category,
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
        cls.url = reverse(
            "dashboard:admin:product-edit", args=[cls.product.pk]
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

    def test_product_edition_with_valid_data(self):
        self.client.force_login(self.admin)

        form_data = {
            "title": "Changed title",
            "slug": "new-product",
            "category": self.category.id,
            "price": 100,
            "status": ProductStatusType.publish.value,
            "brief_description": "Test brief",
            "description": "Test description",
            "stock": 10,
            "discount_percent": 0,
        }
        self.client.post(
            self.url,
            data=form_data,
        )
        self.product.refresh_from_db()

        self.assertEqual(self.product.title, "Changed title")

    def test_image_form_in_context(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertIsInstance(response.context["image_form"], ProductImageForm)


class AdminProductDeleteViewTest(TestCase):
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
            title="Category Test",
            slug="category-test",
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

    def setUp(self):
        self.url = reverse(
            "dashboard:admin:product-delete", args=[self.product.pk]
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

    def test_delete(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, follow=True)
        self.assertContains(response, "حذف محصول با موفقیت انجام شد")
        self.assertFalse(
            ProductModel.objects.filter(pk=self.product.pk).exists()
        )


class AdminAddProductFeatureViewTest(TestCase):
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

        cls.main_category = ProductCategoryModel.objects.create(
            title="Main category", slug="main-category"
        )

        cls.sub_category = ProductCategoryModel.objects.create(
            title="Sub category", slug="sub-category", parent=cls.main_category
        )

        cls.required_feature = CategoryFeature.objects.create(
            category=cls.main_category, name="color", is_required=True
        )

        cls.optional_feature = CategoryFeature.objects.create(
            category=cls.sub_category, name="warranty", is_required=False
        )

        cls.red_option = FeatureOption.objects.create(
            feature=cls.required_feature, value="red"
        )

        cls.blue_option = FeatureOption.objects.create(
            feature=cls.required_feature, value="blue"
        )

        cls.product = ProductModel.objects.create(
            user=cls.user,
            category=cls.sub_category,
            title="Product test",
            slug="product-test",
            description="This is description",
            stock=10,
            discount_percent=20,
            price=100,
            status=ProductStatusType.publish.value,
        )

        cls.url = reverse(
            "dashboard:admin:add-product-feature",
            kwargs={
                "product_id": cls.product.pk,
                "status": cls.product.status,
            },
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

    def test_feature_inheritance_from_parent_categories(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)

        self.assertContains(response, self.required_feature.name)
        self.assertContains(response, self.optional_feature.name)

    def test_feature_creation_logic(self):
        self.client.force_login(self.admin)

        form_data = {
            f"feature_{self.required_feature.id}": self.red_option.id,
            f"feature_{self.optional_feature.id}": "2 years",
        }

        self.client.post(self.url, form_data)

        self.assertEqual(ProductFeature.objects.count(), 2)

        required_feature = ProductFeature.objects.get(
            feature=self.required_feature
        )
        self.assertEqual(required_feature.option, self.red_option)

        optional_feature = ProductFeature.objects.get(
            feature=self.optional_feature
        )
        self.assertEqual(optional_feature.value, "2 years")

    def test_optional_empty_field(self):
        self.client.force_login(self.admin)

        form_data = {
            f"feature_{self.required_feature.id}": self.blue_option.id,
            f"feature_{self.optional_feature.id}": "",
        }

        self.client.post(self.url, form_data)

        self.assertEqual(ProductFeature.objects.count(), 1)

    def test_old_features_deletion(self):
        self.client.force_login(self.admin)

        old_feature = ProductFeature.objects.create(
            product=self.product,
            feature=self.required_feature,
            option=self.red_option,
        )

        form_data = {
            f"feature_{self.required_feature.id}": self.blue_option.id,
            f"feature_{self.optional_feature.id}": "3 years",
        }

        self.client.post(self.url, form_data)

        self.assertFalse(
            ProductFeature.objects.filter(id=old_feature.id).exists()
        )


class AdminEditProductFeatureViewTest(TestCase):
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

        cls.main_category = ProductCategoryModel.objects.create(
            title="Main category", slug="main-category"
        )

        cls.sub_category = ProductCategoryModel.objects.create(
            title="Sub category", slug="sub-category", parent=cls.main_category
        )

        cls.warranty_feature = CategoryFeature.objects.create(
            category=cls.sub_category, name="warranty", is_required=False
        )

        cls.color_feature = CategoryFeature.objects.create(
            category=cls.main_category, name="color", is_required=True
        )

        cls.red_option = FeatureOption.objects.create(
            feature=cls.color_feature, value="red"
        )

        cls.blue_option = FeatureOption.objects.create(
            feature=cls.color_feature, value="blue"
        )

        cls.product = ProductModel.objects.create(
            user=cls.user,
            category=cls.sub_category,
            title="Product test",
            slug="product-test",
            description="This is description",
            stock=10,
            discount_percent=20,
            price=100,
            status=ProductStatusType.publish.value,
        )

        cls.url = reverse(
            "dashboard:admin:edit-product-feature",
            kwargs={"product_id": cls.product.pk},
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

    def test_form_includes_inherited_features(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)

        self.assertContains(response, self.color_feature.name)
        self.assertContains(response, self.warranty_feature.name)

    def test_valid_feature_submission(self):
        self.client.force_login(self.admin)

        form_data = {
            f"feature_{self.color_feature.id}": self.red_option.id,
            f"feature_{self.warranty_feature.id}": "2 years",
        }

        response = self.client.post(self.url, form_data)

        self.assertRedirects(response, reverse("dashboard:admin:product-list"))

        self.assertEqual(ProductFeature.objects.count(), 2)

        color_feature = ProductFeature.objects.get(feature=self.color_feature)
        self.assertEqual(color_feature.option, self.red_option)

        warranty_feature = ProductFeature.objects.get(
            feature=self.warranty_feature
        )
        self.assertEqual(warranty_feature.value, "2 years")

    def test_old_features_deletion(self):
        old_feature = ProductFeature.objects.create(
            product=self.product,
            feature=self.color_feature,
            option=self.blue_option,
        )

        self.client.force_login(self.admin)
        form_data = {f"feature_{self.color_feature.id}": self.red_option.id}

        self.client.post(self.url, form_data)

        self.assertFalse(
            ProductFeature.objects.filter(id=old_feature.id).exists()
        )

    def test_optional_feature_empty_value(self):
        self.client.force_login(self.admin)

        form_data = {
            f"feature_{self.color_feature.id}": self.blue_option.id,
            f"feature_{self.warranty_feature.id}": "",
        }

        self.client.post(self.url, form_data)

        self.assertEqual(ProductFeature.objects.count(), 1)
