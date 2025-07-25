from django.urls import reverse
from rest_framework import serializers

from shop.models import (
    CategoryFeature,
    FeatureOption,
    ProductCategoryModel,
    ProductFeature,
    ProductModel,
)


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategoryModel
        fields = ["id", "title", "slug"]
        ref_name = "ProductCategory"


class FeatureOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureOption
        fields = ["value"]
        ref_name = "FeatureOption"


class CategoryFeatureSerializer(serializers.ModelSerializer):
    options = FeatureOptionSerializer(many=True, source="options.all")

    class Meta:
        model = CategoryFeature
        fields = ["id", "category", "name", "is_required", "options"]
        ref_name = "CategoryFeature"


class ProductFeatureSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="feature.name")
    value = serializers.SerializerMethodField()

    def get_value(self, obj):
        return obj.option.value if obj.option else obj.value

    class Meta:
        model = ProductFeature
        fields = ["name", "value"]
        ref_name = "ProductFeature"


class BaseProductSerializer(serializers.ModelSerializer):
    is_wish = serializers.BooleanField(read_only=True)
    category = ProductCategorySerializer()
    discounted_price = serializers.SerializerMethodField()

    def get_discounted_price(self, obj):
        return obj.get_price()

    class Meta:
        model = ProductModel
        fields = [
            "id",
            "title",
            "slug",
            "image",
            "brief_description",
            "price",
            "discount_percent",
            "discounted_price",
            "avg_rate",
            "category",
            "is_wish",
            "created_date",
            "updated_date",
        ]


class ProductListSerializer(BaseProductSerializer):
    detail_url = serializers.SerializerMethodField()

    class Meta(BaseProductSerializer.Meta):
        fields = BaseProductSerializer.Meta.fields + ["detail_url"]

    def get_detail_url(self, obj):
        request = self.context.get("request")
        if not request:
            return None
        return request.build_absolute_uri(
            reverse("shop:api-v1:product-detail", kwargs={"slug": obj.slug})
        )


class ProductDetailSerializer(BaseProductSerializer):
    features = ProductFeatureSerializer(many=True, source="features.all")

    class Meta(BaseProductSerializer.Meta):
        fields = BaseProductSerializer.Meta.fields + ["features"]


class AddOrRemoveWishlistSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class CategoryNodeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategoryModel
        fields = ["id", "title", "slug", "children"]

    def get_children(self, obj):
        children = obj.get_descendants()
        return CategoryNodeSerializer(
            [item["category"] for item in children],
            many=True,
            context=self.context,
        ).data


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategoryModel
        fields = ["id", "title", "slug", "children"]

    def get_children(self, obj):
        return CategoryNodeSerializer(
            obj.subcategories.all(), many=True, context=self.context
        ).data


class MinPriceSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    min_price = serializers.DecimalField(max_digits=10, decimal_places=0)
    category_slug = serializers.CharField()
    category_title = serializers.CharField()


class PopularProductSerializer(serializers.ModelSerializer):
    discounted_price = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.title")

    class Meta:
        model = ProductModel
        fields = [
            "id",
            "title",
            "category_name",
            "slug",
            "image_url",
            "price",
            "discount_percent",
            "discounted_price",
        ]

    def get_discounted_price(self, obj):
        return obj.get_price()

    def get_image_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if obj.image else None
