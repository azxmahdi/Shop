from django.urls import reverse
from rest_framework import serializers

from shop.models import (
    CategoryFeature,
    FeatureOption,
    ProductCategoryModel,
    ProductFeature,
    ProductImageModel,
    ProductModel,
    ProductStatusType,
)


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategoryModel
        fields = ["id", "title", "slug"]
        ref_name = "AdminProductCategory"


class FeatureOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureOption
        fields = ["id", "value"]
        ref_name = "AdminFeatureOption"


class CategoryFeatureSerializer(serializers.ModelSerializer):
    options = FeatureOptionSerializer(many=True, read_only=True)

    class Meta:
        model = CategoryFeature
        fields = ["id", "name", "is_required", "options"]
        ref_name = "AdminCategoryFeature"


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImageModel
        fields = ["id", "file"]


class ProductFeatureSerializer(serializers.ModelSerializer):
    feature_id = serializers.PrimaryKeyRelatedField(
        source="feature", queryset=CategoryFeature.objects.all()
    )
    option_id = serializers.PrimaryKeyRelatedField(
        source="option",
        queryset=FeatureOption.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ProductFeature
        fields = ["feature_id", "option_id", "value"]
        extra_kwargs = {"value": {"required": False, "allow_blank": True}}
        ref_name = "AdminProductFeature"


class ProductSerializer(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField()
    images = ProductImageSerializer(
        source="product_images", many=True, read_only=True
    )
    features = ProductFeatureSerializer(
        many=True, required=False, write_only=True
    )
    category = ProductCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategoryModel.objects.filter(parent__isnull=False),
        source="category",
        write_only=True,
    )

    class Meta:
        model = ProductModel
        fields = [
            "id",
            "category",
            "category_id",
            "title",
            "slug",
            "image",
            "images",
            "description",
            "brief_description",
            "stock",
            "status",
            "price",
            "discount_percent",
            "features",
            "detail_url",
            "created_date",
            "updated_date",
        ]
        extra_kwargs = {
            "slug": {"required": False},
            "status": {"default": ProductStatusType.not_completed.value},
        }

    def create(self, validated_data):
        features_data = validated_data.pop("features", [])
        images_data = self.context["request"].FILES.getlist("images")

        product = ProductModel.objects.create(
            **validated_data, user=self.context["request"].user
        )

        for feature_data in features_data:
            ProductFeature.objects.create(product=product, **feature_data)

        for image in images_data:
            ProductImageModel.objects.create(product=product, file=image)

        return product

    def get_detail_url(self, obj):
        request = self.context.get("request")
        if request is None:
            return None

        return request.build_absolute_uri(
            reverse(
                "dashboard:api-v1:admin:product-detail", kwargs={"pk": obj.pk}
            )
        )
