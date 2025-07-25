from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import Profile


class SecuritySerializer(serializers.Serializer):

    old_password = serializers.CharField(max_length=300, write_only=True)
    new_password = serializers.CharField(max_length=300, write_only=True)
    new_password1 = serializers.CharField(max_length=300, write_only=True)

    class Meta:
        ref_name = "AdminSecurity"

    def validate(self, attrs):

        new_password = attrs["new_password"]
        new_password1 = attrs["new_password1"]
        old_password = attrs["old_password"]

        if new_password != new_password1:
            raise serializers.ValidationError(
                {"new_password": "رمز عبور جدید با تکرار آن برابر نیست"}
            )

        user = self.get_user()
        if not user.check_password(old_password):
            raise serializers.ValidationError(
                {"old_password": "رمز عبور قبلی صحیح نیست"}
            )

        try:
            validate_password(password=new_password)
        except ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)}
            )

        return super().validate(attrs)

    def get_user(self):

        return get_user_model().objects.get(pk=self.context["request"].user.id)


class ProfileSerializer(serializers.ModelSerializer):

    user = serializers.CharField(label="email", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "user",
            "first_name",
            "last_name",
            "phone_number",
            "image",
            "created_date",
            "updated_date",
        ]
        ref_name = "AdminProfile"
