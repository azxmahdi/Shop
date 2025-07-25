from django.urls import path

from .. import views

urlpatterns = [
    path(
        "security/edit/", views.SecurityEditAPI.as_view(), name="security-edit"
    ),
    path("profile/edit/", views.ProfileEditAPI.as_view(), name="profile-edit"),
]
