from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import (
    CategoryFeature,
    FeatureOption,
    ProductCategoryModel,
    ProductImageModel,
    ProductModel,
    ProductStatusType,
    WishlistProductModel,
)

User = get_user_model()


class TestProductStatusType(TestCase):
    def test_choices_structure(self):
        expected_choices = [
            (1, "منتشر شده"),
            (2, "عدم انتشار"),
            (3, "به صورت کامل ایجاد نشده"),
        ]
        self.assertEqual(expected_choices, ProductStatusType.choices)


class TestProductCategory(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.root = ProductCategoryModel.objects.create(
            title="Root", slug="root"
        )
        cls.level1 = ProductCategoryModel.objects.create(
            parent=cls.root, title="Level 1", slug="level-1"
        )
        cls.level2 = ProductCategoryModel.objects.create(
            parent=cls.level1, title="Level 2", slug="level-2"
        )

    def test_category_creation(self):

        self.assertEqual(self.root.title, "Root")
        self.assertEqual(self.root.slug, "root")
        self.assertIsNone(self.root.parent)

    def test_unique_slug(self):

        category2 = ProductCategoryModel(title="Invalid category", slug="root")
        with self.assertRaises(ValidationError):
            category2.full_clean()

    def test_multi_level_hierarchy(self):

        self.assertEqual(self.level2.parent, self.level1)
        self.assertEqual(self.level1.parent, self.root)

    def test_get_ancestors_func(self):

        ancestors = self.level2.get_ancestors()
        self.assertIn(self.level1, ancestors)
        self.assertIn(self.root, ancestors)

    def test_get_all_subcategories(self):

        subcategories = self.root.get_all_subcategories()
        self.assertIn(self.level1, subcategories)
        self.assertIn(self.level2, subcategories)

    def test_get_cheapest_product_price_func(self):
        user = User.objects.create_superuser(
            email="test_shop@example.com", password="TestShop123@"
        )
        ProductModel.objects.create(
            user=user,
            category=self.root,
            title="product for category Root",
            slug="product-for-category-root",
            description="This is description",
            stock=50,
            price=1000,
            discount_percent=10,
        )
        ProductModel.objects.create(
            user=user,
            category=self.level1,
            title="product for category Level 1",
            slug="product-for-category-level-1",
            description="This is description",
            stock=5,
            price=500,
            discount_percent=10,
        )

        ProductModel.objects.create(
            user=user,
            category=self.level2,
            title="product for category Level 2",
            slug="product-for-category-level-2",
            description="This is description",
            stock=5,
            price=1100,
            discount_percent=10,
        )
        cheapest_product = self.root.get_cheapest_product_price()
        self.assertEqual(cheapest_product, 500)

    def test_get_all_features_is_required_func(self):
        CategoryFeature.objects.create(
            category=self.level2, name="Feature test 1", is_required=True
        )
        CategoryFeature.objects.create(
            category=self.level2, name="Feature test 2", is_required=False
        )
        CategoryFeature.objects.create(
            category=self.level1, name="Feature test 1", is_required=True
        )

        CategoryFeature.objects.create(
            category=self.root, name="Feature test 1", is_required=True
        )
        CategoryFeature.objects.create(
            category=self.root, name="Feature test 1", is_required=False
        )

        features_is_required = self.level2.get_all_features_is_required()
        self.assertEqual(features_is_required.count(), 3)

    def test_get_all_features(self):
        CategoryFeature.objects.create(
            category=self.level2, name="Feature test 1", is_required=False
        )
        CategoryFeature.objects.create(
            category=self.level2, name="Feature test 2", is_required=True
        )
        CategoryFeature.objects.create(
            category=self.level1, name="Feature test 1", is_required=False
        )

        CategoryFeature.objects.create(
            category=self.root, name="Feature test 1", is_required=True
        )
        CategoryFeature.objects.create(
            category=self.root, name="Feature test 1", is_required=False
        )
        all_features = self.level2.get_all_features()
        self.assertEqual(all_features.count(), 5)


class TestCategoryFeature(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = ProductCategoryModel.objects.create(
            title="Test category", slug="test-category"
        )

    def test_category_feature_creation(self):
        category_feature = CategoryFeature.objects.create(
            category=self.category, name="Test feature", is_required=True
        )
        self.assertEqual(category_feature.name, "Test feature")
        self.assertTrue(category_feature.is_required)


class TestFeatureOption(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = ProductCategoryModel.objects.create(
            title="Test category", slug="test-category"
        )
        cls.feature = CategoryFeature.objects.create(
            category=cls.category, name="Test feature", is_required=True
        )

    def test_category_feature_creation(self):
        feature_option = FeatureOption.objects.create(
            feature=self.feature, value="Test value"
        )
        self.assertEqual(feature_option.feature, self.feature)
        self.assertEqual(feature_option.value, "Test value")


class TestProduct(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(
            email="test_shop@example.com", password="TestShop123@"
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

    def test_product_creation(self):
        self.assertEqual(self.product.user, self.user)
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.title, "Product test")
        self.assertEqual(self.product.slug, "product-test")
        self.assertEqual(self.product.description, "This is description")
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(self.product.price, 100)

    def test_get_price_func(self):
        expected_price = 80
        self.assertEqual(self.product.get_price(), expected_price)

    def test_is_discounted_func(self):
        self.assertTrue(self.product.is_discounted())

    def test_is_published_func(self):
        self.assertTrue(self.product.is_published())

    def test_is_not_completed_func(self):
        self.assertFalse(self.product.is_not_completed())

    def test_is_new_func(self):
        self.assertTrue(self.product.is_new())


class TestProductFeature(TestCase):
    pass


class TestProductImage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(
            email="test_shop@example.com", password="TestShop123@"
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
            price=Decimal("100"),
            status=ProductStatusType.publish.value,
        )
        cls.image = ProductImageModel.objects.create(
            product=cls.product, file="path/to/image1.jpg"
        )

    def test_product_image_creation(self):
        self.assertEqual(self.image.product, self.product)
        self.assertEqual(self.image.file, "path/to/image1.jpg")


class TestWishlistProduct(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(
            email="test_shop@example.com", password="TestShop123@"
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
            price=Decimal("500"),
            status=ProductStatusType.publish.value,
        )

    def wishlist_product_creation(self):
        wishlist = WishlistProductModel.objects.create(
            user=self.user, product=self.product
        )
        self.assertEqual(wishlist.user, self.user)
        self.assertEqual(wishlist.product, self.product)
