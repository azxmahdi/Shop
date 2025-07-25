from django.urls import path

from . import views

urlpatterns = [
    path(
        "submit-review/", views.SubmitReviewAPI.as_view(), name="submit-review"
    )
]
