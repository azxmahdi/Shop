from rest_framework import serializers

from accounts.models import Profile
from website.models import ContactModel, JobTitle, NewsLetter, TeamMembers


class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTitle
        fields = ["id", "title"]


class ProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["full_name", "image"]
        ref_name = "WebsiteProfile"

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class TeamMemberSerializer(serializers.ModelSerializer):
    job_titles = JobTitleSerializer(many=True, source="job_title.all")
    profile = ProfileSerializer()

    class Meta:
        model = TeamMembers
        fields = [
            "id",
            "profile",
            "job_titles",
            "description",
            "facebook_link",
            "twitter_link",
            "status",
            "created_date",
            "updated_date",
        ]


class ContactSerializer(serializers.ModelSerializer):

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


class NewsLetterSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsLetter
        fields = ["id", "email", "created_date", "updated_date"]
        read_only_fields = ("id", "created_date", "updated_date")
        ref_name = "WebsiteNewsLetter"
