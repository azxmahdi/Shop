from django.urls import include, path, re_path

from . import views

app_name = "shop"

urlpatterns = [
    path("api/v1/", include("shop.api.v1.urls"), name="api-v1"),
    path(
        "product/grid/",
        views.ShopProductGridView.as_view(),
        name="product-grid",
    ),
    re_path(
        r"product/(?P<slug>[-\w]+)/detail/",
        views.ShopProductDetailView.as_view(),
        name="product-detail",
    ),
    path(
        "categories/sidebar/",
        views.CategoriesSidebar.as_view(),
        name="categories-sidebar",
    ),
    path(
        "add-or-remove-wishlist/",
        views.AddOrRemoveWishlistView.as_view(),
        name="add-or-remove-wishlist",
    ),
]
