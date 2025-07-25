from rest_framework import serializers

from review.models import ReviewModel


class ReviewSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ReviewModel
        fields = ["id", "user", "full_name", "product", "description", "rate"]
        read_only_fields = ("id", "user")
        ref_name = "Review"

    def create(self, validated_data):
        validated_data["user"] = self.context.get("request").user
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context["request"].user
        product = attrs.get("product")

        if ReviewModel.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError(
                {"detail": "شما قبلاً برای این محصول دیدگاه ثبت کرده‌اید"},
                code="duplicate_review",
            )

        return attrs

    def get_full_name(self, obj):
        return obj.user.user_profile.get_fullname()
