from rest_framework import serializers

from shop.models import WishlistProductModel


class WishlistSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.email")
    product = serializers.CharField(source="product.title")

    class Meta:
        model = WishlistProductModel
        fields = ["id", "user", "product"]
