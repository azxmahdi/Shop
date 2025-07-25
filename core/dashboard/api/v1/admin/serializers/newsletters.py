from rest_framework import serializers

from website.models import NewsLetter


class NewsLetterSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsLetter
        fields = ["id", "email", "created_date", "updated_date"]
        read_only_fields = ("id", "created_date", "updated_date")
        ref_name = "DashboardNewsLetter"
