from django.urls import path

from .. import views

urlpatterns = [
    path("review/list/", views.ReviewListAPI.as_view(), name="review-list"),
    path(
        "review/detail/<int:pk>/",
        views.ReviewRetrieveUpdateAPI.as_view(),
        name="review-detail",
    ),
]
