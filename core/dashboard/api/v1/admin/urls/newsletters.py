from django.urls import path

from .. import views

urlpatterns = [
    path(
        "newsLetter/list/",
        views.NewsletterListAPI.as_view(),
        name="newsLetter-list",
    ),
    path(
        "newsLetter/delete/<int:pk>/",
        views.NewsletterDeleteAPI.as_view(),
        name="newsLetter-list",
    ),
]
