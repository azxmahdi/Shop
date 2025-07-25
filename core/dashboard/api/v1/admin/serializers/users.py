from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import UserType

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "type",
            "status_display",
            "is_active",
            "is_verified",
            "created_date",
            "updated_date",
        ]
        read_only_fields = (
            "id",
            "email",
            "created_date",
            "updated_date",
            "status_display",
        )

    def get_status_display(self, obj):
        return obj.get_status_display()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if not request:
            return

        if request.user.type == UserType.admin.value:
            if "type" in self.fields:
                self.fields["type"].read_only = True

    def get_status_display(self, obj):
        return {
            "id": obj.type,
            "title": obj.get_status()["title"],
            "label": obj.get_status()["label"],
        }
