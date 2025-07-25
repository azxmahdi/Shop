from django.utils import timezone
from rest_framework import serializers

from order.models import CouponModel, UserAddressModel


class OrderCheckOutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(required=True)
    coupon = serializers.CharField(required=False, allow_blank=True)

    def validate_address_id(self, value):
        user = self.context["request"].user
        try:
            return UserAddressModel.objects.get(id=value, user=user)
        except UserAddressModel.DoesNotExist:
            raise serializers.ValidationError(
                "آدرس انتخاب شده معتبر نیست یا به کاربر تعلق ندارد"
            )

    def validate_coupon(self, value):
        if not value:
            return None

        try:
            coupon = CouponModel.objects.get(code=value)
        except CouponModel.DoesNotExist:
            raise serializers.ValidationError("کد تخفیف معتبر نیست")

        validation_errors = []

        if coupon.expiration_date and coupon.expiration_date < timezone.now():
            validation_errors.append("کد تخفیف منقضی شده است")

        if coupon.used_by.count() >= coupon.max_limit_usage:
            validation_errors.append("محدودیت تعداد استفاده از کد تخفیف")

        if self.context["request"].user in coupon.used_by.all():
            validation_errors.append(
                "شما قبلاً از این کد تخفیف استفاده کرده‌اید"
            )

        if validation_errors:
            raise serializers.ValidationError(", ".join(validation_errors))

        return coupon


class ValidateCouponSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, attrs):
        code = attrs.get("code")
        request = self.context.get("request")

        if not code:
            return attrs

        try:
            coupon = CouponModel.objects.get(code=code)
        except CouponModel.DoesNotExist:
            raise serializers.ValidationError({"code": "کد تخفیف معتبر نیست"})

        errors = []

        if coupon.expiration_date and coupon.expiration_date < timezone.now():
            errors.append("کد تخفیف منقضی شده است")

        if coupon.used_by.count() >= coupon.max_limit_usage:
            errors.append("محدودیت تعداد استفاده از کد تخفیف")

        if request.user in coupon.used_by.all():
            errors.append("شما قبلاً از این کد تخفیف استفاده کرده‌اید")

        if errors:
            raise serializers.ValidationError({"detail": errors})

        attrs["coupon"] = coupon
        return attrs
