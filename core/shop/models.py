from datetime import timedelta
from decimal import Decimal

from ckeditor_uploader.fields import RichTextUploadingField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class ProductStatusType(models.IntegerChoices):
    publish = 1, ("منتشر شده")
    draft = 2, ("عدم انتشار")
    not_completed = 3, ("به صورت کامل ایجاد نشده")


class ProductCategoryModel(models.Model):
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, unique=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return self.title

    def get_ancestors(self):
        """Get all parent categories from the root to this category"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors

    def get_all_features_is_required(self):
        """Get all the properties of this category and its parent categories"""
        from .models import CategoryFeature

        features = CategoryFeature.objects.filter(
            category=self, is_required=True
        )
        for ancestor in self.get_ancestors():
            features |= CategoryFeature.objects.filter(
                category=ancestor, is_required=True
            )
        return features

    def get_all_features(self):
        """Get all the properties of this category and its parent categories"""
        from .models import CategoryFeature

        features = CategoryFeature.objects.filter(category=self)
        for ancestor in self.get_ancestors():
            features |= CategoryFeature.objects.filter(category=ancestor)
        return features

    def get_all_subcategories(self):
        """Collect all subcategories recursively"""
        subcategories = list(self.subcategories.all())
        for subcategory in self.subcategories.all():
            subcategories.extend(subcategory.get_all_subcategories())
        return subcategories

    def get_cheapest_product_price(self):
        """Finding the cheapest product across all subcategories"""
        from django.db.models import Min

        all_categories = [self] + self.get_all_subcategories()
        category_ids = [cat.id for cat in all_categories]
        result = ProductModel.objects.filter(
            category_id__in=category_ids
        ).aggregate(min_price=Min("price"))

        return result["min_price"]

    def get_descendants(self):

        descendants = []
        for child in self.subcategories.all():
            descendants.append(
                {"category": child, "children": child.get_descendants()}
            )
        return descendants


class CategoryFeature(models.Model):
    category = models.ForeignKey(
        ProductCategoryModel,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    is_required = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category.title} - {self.name}"


class FeatureOption(models.Model):
    feature = models.ForeignKey(
        CategoryFeature,
        on_delete=models.CASCADE,
        related_name="options",
    )
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.value


class ProductModel(models.Model):
    user = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.PROTECT,
        related_name="products",
    )
    category = models.ForeignKey(
        ProductCategoryModel,
        on_delete=models.PROTECT,
        related_name="products",
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, unique=True)
    image = models.ImageField(
        default="/default/product-image.png", upload_to="product/img/"
    )
    description = RichTextUploadingField()
    brief_description = models.TextField(
        null=True,
        blank=True,
    )
    stock = models.PositiveIntegerField(default=0)
    status = models.IntegerField(
        choices=ProductStatusType.choices,
        default=ProductStatusType.draft.value,
    )
    price = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=0,
    )
    discount_percent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    avg_rate = models.FloatField(default=0.0)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["status", "-created_date", "-avg_rate"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self):
        return self.title

    def get_price(self):
        discount_amount = self.price * Decimal(self.discount_percent / 100)
        discounted_amount = self.price - discount_amount
        return round(discounted_amount)

    def is_discounted(self):
        return self.discount_percent != 0

    def is_published(self):
        return self.status == ProductStatusType.publish.value

    def is_not_completed(self):
        return self.status == ProductStatusType.not_completed.value

    def is_new(self):
        return self.created_date >= timezone.now() - timedelta(weeks=1)

    def get_status(self):
        return {
            "id": self.status,
            "title": ProductStatusType(self.status).name,
            "label": ProductStatusType(self.status).label,
        }


class ProductFeature(models.Model):
    product = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        related_name="features",
    )
    feature = models.ForeignKey(
        CategoryFeature,
        on_delete=models.CASCADE,
    )
    value = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    option = models.ForeignKey(
        FeatureOption,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.product.title} - {self.feature.name}"


class ProductImageModel(models.Model):
    product = models.ForeignKey(
        ProductModel, on_delete=models.CASCADE, related_name="product_images"
    )
    file = models.ImageField(upload_to="product/extra-img/")

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]


class WishlistProductModel(models.Model):
    user = models.ForeignKey("accounts.CustomUser", on_delete=models.PROTECT)
    product = models.ForeignKey(
        ProductModel, on_delete=models.CASCADE, related_name="in_wishlists"
    )

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.product.title
