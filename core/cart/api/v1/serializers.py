from rest_framework import serializers

from shop.models import ProductModel


class AddOrRemoveOrCheckIsProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class UpdateProductQuantitySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()


class ProductSerializer(serializers.ModelSerializer):

    category = serializers.CharField(label="title")
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ProductModel
        fields = [
            "id",
            "category",
            "title",
            "slug",
            "image",
            "description",
            "brief_description",
            "stock",
            "price",
            "status",
            "status_display",
            "price",
            "discount_percent",
            "avg_rate",
        ]
        read_only_fields = fields

    def get_status_display(self, obj):
        return obj.get_status_display()
