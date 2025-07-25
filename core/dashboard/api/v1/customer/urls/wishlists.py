from django.urls import path

from .. import views

urlpatterns = [
    path(
        "wishlist/list/", views.WishlistListAPI.as_view(), name="wishlist-list"
    ),
    path(
        "wishlist/<int:pk>/delete/",
        views.WishlistDeleteAPI.as_view(),
        name="wishlist-delete",
    ),
]
