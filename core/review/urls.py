from django.urls import include, path

from . import views

app_name = "review"

urlpatterns = [
    path("api/v1/", include("review.api.v1.urls"), name="api-v1"),
    path(
        "submit-review/",
        views.SubmitReviewView.as_view(),
        name="submit-review",
    ),
]
