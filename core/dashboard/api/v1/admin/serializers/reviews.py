from django.urls import reverse
from rest_framework import serializers

from review.models import ReviewModel


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(label="email", read_only=True)
    product = serializers.CharField(label="title", read_only=True)
    status_display = serializers.SerializerMethodField()
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = ReviewModel
        fields = [
            "id",
            "user",
            "product",
            "description",
            "rate",
            "status_display",
            "status",
            "detail_url",
            "created_date",
            "updated_date",
        ]
        read_only_fields = (
            "id",
            "user",
            "product",
            "description",
            "rate",
            "status_display",
            "detail_url",
            "created_date",
            "updated_date",
        )
        extra_kwargs = {"status": {"write_only": True}}
        ref_name = "AdminReview"

    def get_status_display(self, obj):
        return {
            "id": obj.status,
            "title": obj.get_status()["title"],
            "label": obj.get_status()["label"],
        }

    def get_detail_url(self, obj):
        request = self.context.get("request")
        if not request:
            return None
        return request.build_absolute_uri(
            reverse(
                "dashboard:api-v1:admin:review-detail", kwargs={"pk": obj.pk}
            )
        )
