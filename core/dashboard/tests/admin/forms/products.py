from io import BytesIO

from django import forms
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from accounts.models import UserType
from dashboard.admin.forms import (
    ProductFeatureForm,
    ProductForm,
    ProductImageForm,
)
from shop.models import (
    CategoryFeature,
    FeatureOption,
    ProductCategoryModel,
    ProductModel,
    ProductStatusType,
)

User = get_user_model()


class AdminProductFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        category_parent = ProductCategoryModel.objects.create(
            title="test category parent", slug="test-category-parent"
        )
        cls.category = ProductCategoryModel.objects.create(
            parent=category_parent, title="test category", slug="test-category"
        )
        cls.valid_data = {
            "category": cls.category.pk,
            "title": "title_product",
            "slug": "title-product",
            "image": "image.jpg",
            "description": "This is a test description",
            "brief_description": "This is a test brief description",
            "stock": 10,
            "status": ProductStatusType.publish.value,
            "price": 100,
            "discount_percent": 5,
        }
        cls.form = ProductForm(cls.valid_data)

    def test_product_form_with_valid_data(self):
        self.assertTrue(self.form.is_valid())

    def test_product_form_with_invalid_data(self):
        invalid_data = self.valid_data.copy()
        invalid_data["title"] = ""
        form = ProductForm(invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)


class AdminProductImageFormTest(TestCase):
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
            title="Product test",
            slug="product-test",
            description="This is description",
            stock=10,
            discount_percent=20,
            price=100,
            status=ProductStatusType.publish.value,
        )

        image = Image.new("RGB", (100, 100), color="red")
        image_buffer = BytesIO()
        image.save(image_buffer, format="jpeg")
        image_buffer.seek(0)

        cls.test_image_file = SimpleUploadedFile(
            name="test_image.jpg",
            content=image_buffer.getvalue(),
            content_type="image/jpeg",
        )

        cls.valid_files_data = {
            "file": cls.test_image_file,
        }

        cls.valid_data = {}

    def test_product_image_form_with_valid_data(self):
        form = ProductImageForm(
            data=self.valid_data, files=self.valid_files_data
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_product_image_form_with_invalid_data(self):
        invalid_files_data = self.valid_files_data.copy()
        invalid_files_data["file"] = ""
        form = ProductImageForm(data=self.valid_data, files=invalid_files_data)
        self.assertFalse(form.is_valid())
        self.assertIn("file", form.errors)


class AdminProductFeatureFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            email="admin@gmail.com",
            password="Admin123/",
            type=UserType.admin.value,
        )

        cls.category_parent = ProductCategoryModel.objects.create(
            title="Digital devices", slug="digital-devices"
        )
        cls.category = ProductCategoryModel.objects.create(
            parent=cls.category_parent, title="Mobile", slug="mobile"
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
        cls.color_feature = CategoryFeature.objects.create(
            category=cls.category_parent, name="Color", is_required=True
        )
        cls.number_of_camera_feature = CategoryFeature.objects.create(
            category=cls.category,
            name="Number of camera feature",
            is_required=False,
        )
        cls.memory_feature = CategoryFeature.objects.create(
            category=cls.category, name="Memory", is_required=True
        )
        cls.option_memory1 = FeatureOption.objects.create(
            feature=cls.memory_feature, value="64GB"
        )
        cls.option_memory2 = FeatureOption.objects.create(
            feature=cls.memory_feature, value="128GB"
        )
        cls.charging_speed_feature = CategoryFeature.objects.create(
            category=cls.category, name="Charging speed", is_required=False
        )
        cls.option_charging_speed1 = FeatureOption.objects.create(
            feature=cls.charging_speed_feature, value="15W"
        )
        cls.option_charging_speed2 = FeatureOption.objects.create(
            feature=cls.charging_speed_feature, value="33W"
        )

    def test_form_initialization_and_field_creation(self):
        form = ProductFeatureForm(product_id=self.product.id)
        self.assertIn(f"feature_{self.color_feature.id}", form.fields)
        self.assertIn(f"feature_{self.memory_feature.id}", form.fields)
        self.assertIn(f"feature_{self.charging_speed_feature.id}", form.fields)

        color_field = form.fields[f"feature_{self.color_feature.id}"]
        self.assertIsInstance(color_field, forms.CharField)

        number_of_camera_field = form.fields[
            f"feature_{self.number_of_camera_feature.id}"
        ]
        self.assertIsInstance(number_of_camera_field, forms.CharField)

        memory_field = form.fields[f"feature_{self.memory_feature.id}"]
        self.assertIsInstance(memory_field, forms.ChoiceField)
        self.assertEqual(len(memory_field.choices), 2)
        self.assertIn(
            (self.option_memory1.id, self.option_memory1.value),
            memory_field.choices,
        )
        self.assertIn(
            (self.option_memory2.id, self.option_memory2.value),
            memory_field.choices,
        )
        self.assertNotIn(("", "----"), memory_field.choices)

        charging_speed_field = form.fields[
            f"feature_{self.charging_speed_feature.id}"
        ]
        self.assertIsInstance(charging_speed_field, forms.ChoiceField)
        self.assertEqual(len(charging_speed_field.choices), 3)
        self.assertIn(
            (
                self.option_charging_speed1.id,
                self.option_charging_speed1.value,
            ),
            charging_speed_field.choices,
        )
        self.assertIn(
            (
                self.option_charging_speed2.id,
                self.option_charging_speed2.value,
            ),
            charging_speed_field.choices,
        )
        self.assertIn(("", "----"), charging_speed_field.choices)

    def test_form_with_valid_data(self):
        data = {
            f"feature_{self.color_feature.id}": "Red",
            f"feature_{self.number_of_camera_feature.id}": "4",
            f"feature_{self.memory_feature.id}": self.option_memory1.id,
            f"feature_{self.charging_speed_feature.id}": self.option_charging_speed1.id,
        }
        form = ProductFeatureForm(product_id=self.product.id, data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_with_valid_data_optional_fields_empty(self):
        data = {
            f"feature_{self.color_feature.id}": "Red",
            f"feature_{self.number_of_camera_feature.id}": "",
            f"feature_{self.memory_feature.id}": self.option_memory1.id,
            f"feature_{self.charging_speed_feature.id}": "",
        }
        form = ProductFeatureForm(product_id=self.product.id, data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_with_missing_required_char_field(self):
        data = {
            f"feature_{self.color_feature.id}": "",
            f"feature_{self.number_of_camera_feature.id}": "4",
            f"feature_{self.memory_feature.id}": self.option_memory1.id,
            f"feature_{self.charging_speed_feature.id}": self.option_charging_speed2.id,
        }
        form = ProductFeatureForm(product_id=self.product.id, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn(f"feature_{self.color_feature.id}", form.errors)
        self.assertEqual(
            form.errors[f"feature_{self.color_feature.id}"],
            ["This field is required."],
        )

    def test_form_with_missing_required_choice_field(self):
        data = {
            f"feature_{self.color_feature.id}": "Red",
            f"feature_{self.number_of_camera_feature.id}": "4",
            f"feature_{self.charging_speed_feature.id}": self.option_charging_speed1.id,
        }
        form = ProductFeatureForm(product_id=self.product.id, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn(f"feature_{self.memory_feature.id}", form.errors)
        self.assertEqual(
            form.errors[f"feature_{self.memory_feature.id}"],
            ["This field is required."],
        )

    def test_form_with_invalid_data(self):
        data = {
            f"feature_{self.color_feature.id}": "Red",
            f"feature_{self.number_of_camera_feature.id}": "4",
            f"feature_{self.memory_feature.id}": self.option_memory1.id,
            f"feature_{self.charging_speed_feature.id}": 999999,
        }
        form = ProductFeatureForm(product_id=self.product.id, data=data)
        self.assertFalse(form.is_valid(), form.errors)
        self.assertIn(f"feature_{self.charging_speed_feature.id}", form.errors)
        self.assertEqual(
            form.errors[f"feature_{self.charging_speed_feature.id}"],
            [
                "Select a valid choice. 999999 is not one of the available choices."
            ],
        )
