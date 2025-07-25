from django.contrib import admin

from .models import ContactModel, JobTitle, NewsLetter, TeamMembers


@admin.register(ContactModel)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "phone_number",
        "subject",
        "content",
    )


@admin.register(TeamMembers)
class TeamMembersAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "description",
        "facebook_link",
        "twitter_link",
        "created_date",
        "updated_date",
        "status",
    )


@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ("id", "title")


@admin.register(NewsLetter)
class NewsLetterAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "created_date")
