from django.urls import reverse
from rest_framework import serializers

from order.models import UserAddressModel


class UserAddressSerializer(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = UserAddressModel
        fields = [
            "id",
            "user",
            "address",
            "state",
            "city",
            "zip_code",
            "detail_url",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ("id", "user", "detail_url")

    def create(self, validated_data):
        validated_data["user"] = self.context.get("request").user
        return super().create(validated_data)

    def get_detail_url(self, obj):
        request = self.context.get("request")
        if request is None:
            return None

        return request.build_absolute_uri(
            reverse(
                "dashboard:api-v1:customer:address-detail",
                kwargs={"pk": obj.pk},
            )
        )
