from django.urls import path, re_path

from . import views

app_name = "api-v1"

urlpatterns = [
    path(
        "category-feature/list/",
        views.CategoryFeatureAPI.as_view(),
        name="category-feature-list",
    ),
    path("product/grid/", views.ProductGridAPI.as_view(), name="product-grid"),
    re_path(
        r"product/(?P<slug>[-\w]+)/detail/",
        views.ProductDetailAPI.as_view(),
        name="product-detail",
    ),
    path(
        "add-or-remove-wishlist/",
        views.AddOrRemoveWishlistAPI.as_view(),
        name="add-or-remove-wishlist",
    ),
    path(
        "categories/sidebar/",
        views.CategoriesSidebarAPI.as_view(),
        name="categories-sidebar",
    ),
]
