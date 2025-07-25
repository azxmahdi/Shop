from django.urls import path

from ..views import UserDeleteAPIView, UserListAPI, UserUpdateAPI

urlpatterns = [
    path("user/list/", UserListAPI.as_view(), name="user-list"),
    path("user/edit/<int:pk>/", UserUpdateAPI.as_view(), name="user-edit"),
    path(
        "user/delete/<int:pk>/",
        UserDeleteAPIView.as_view(),
        name="user-delete",
    ),
]
