from django.urls import path

from . import views

app_name = "api-v1"

urlpatterns = [
    path(
        "team-member/list/",
        views.TeamMemberListAPI.as_view(),
        name="team-member-list",
    ),
    path(
        "contact/create/",
        views.ContactCreateAPI.as_view(),
        name="contact-create",
    ),
    path(
        "newsletter/create/",
        views.NewsletterCreateAPI.as_view(),
        name="newsletter-create",
    ),
]
