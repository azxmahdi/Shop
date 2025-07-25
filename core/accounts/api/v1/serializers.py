from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import Profile
from accounts.validators import PasswordValidator

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=300, write_only=True)
    confirm_password = serializers.CharField(max_length=300, write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "confirm_password"]

    def create(self, validated_data):
        validated_data.pop("confirm_password", None)
        return User.objects.create_user(**validated_data)

    def validate(self, attrs):
        password = attrs["password"]
        confirm_password = attrs["confirm_password"]
        if password != confirm_password:
            raise serializers.ValidationError(
                {"password": "پسورد و تایید پسورد با هم برابر نیستند"}
            )

        validator = PasswordValidator()
        try:
            validator.validate(password)
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return super().validate(attrs)


class ResendEmailConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={"invalid": "فرمت ایمیل اشتباه است."}
    )

    def validate(self, attrs):
        email = attrs["email"]
        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "کاربری با این ایمیل وجود ندارد."}
            )

        if user.is_verified:
            raise serializers.ValidationError(
                {"detail": "این اکانت فعال است."}
            )

        attrs["user"] = user
        return super().validate(attrs)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True, validators=[validate_password]
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("پسورد قدیمی نادرست است.")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(label="email", read_only=True)

    class Meta:
        model = Profile
        fields = ["user", "first_name", "last_name", "image", "phone_number"]
        ref_name = "AccountsProfile"


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):

        validated_data = super().validate(attrs)
        validated_data["email"] = self.user.email

        return validated_data
