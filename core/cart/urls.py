from django.urls import include, path

from . import views

app_name = "cart"

urlpatterns = [
    path(
        "session/add-product/",
        views.SessionAddProductView.as_view(),
        name="session-add-product",
    ),
    path(
        "session/remove-product/",
        views.SessionRemoveProductView.as_view(),
        name="session-remove-product",
    ),
    path(
        "session/update-product-quantity/",
        views.SessionUpdateProductQuantityView.as_view(),
        name="session-update-product-quantity",
    ),
    path(
        "session/check-is-product/",
        views.CheckIsProductView.as_view(),
        name="session-check-is-product",
    ),
    path(
        "session/update-product-quantity-detail/",
        views.SessionUpdateProductQuantityDetailView.as_view(),
        name="session-update-product-quantity-detail",
    ),
    path("summary/", views.CartSummaryView.as_view(), name="cart-summary"),
    path("api/v1/", include("cart.api.v1.urls"), name="api-v1"),
]
