from django.urls import reverse
from rest_framework import serializers

from website.models import ContactModel


class ContactSerializer(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = ContactModel
        fields = [
            "id",
            "full_name",
            "email",
            "phone_number",
            "subject",
            "content",
            "is_seen",
            "created_date",
            "updated_date",
            "detail_url",
        ]

    def get_detail_url(self, obj):
        request = self.context.get("request")
        if request is None:
            return None

        return request.build_absolute_uri(
            reverse(
                "dashboard:api-v1:admin:contact-detail", kwargs={"pk": obj.pk}
            )
        )


class ContactDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactModel
        fields = [
            "id",
            "full_name",
            "email",
            "phone_number",
            "subject",
            "content",
            "is_seen",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ("id", "is_seen", "created_date", "updated_date")
