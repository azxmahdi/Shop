from django.urls import reverse
from rest_framework import serializers

from order.models import CouponModel


class CouponSerializer(serializers.ModelSerializer):
    user = serializers.CharField(label="email", read_only=True)
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = CouponModel
        fields = [
            "id",
            "user",
            "code",
            "discount_percent",
            "max_limit_usage",
            "used_by",
            "expiration_date",
            "created_date",
            "updated_date",
            "detail_url",
        ]
        read_only_fields = (
            "id",
            "user",
            "created_date",
            "updated_date",
            "used_by",
        )

    def create(self, validated_data):
        validated_data["user"] = self.context.get("request").user
        return super().create(validated_data)

    def get_detail_url(self, obj):
        request = self.context.get("request")
        if request is None:
            return None

        return request.build_absolute_uri(
            reverse(
                "dashboard:api-v1:admin:coupon-detail", kwargs={"pk": obj.pk}
            )
        )
