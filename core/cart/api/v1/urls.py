from django.urls import path

from . import views

app_name = "api-v1"

urlpatterns = [
    path("add-product/", views.AddProductView.as_view(), name="add-product"),
    path(
        "remove-product/",
        views.RemoveProductView.as_view(),
        name="remove-product",
    ),
    path(
        "update-product-quantity/",
        views.UpdateProductQuantityView.as_view(),
        name="update-product-quantity",
    ),
    path("summery/", views.CartSummaryView.as_view(), name="summery"),
    path(
        "check-is-product/",
        views.CheckIsProductView.as_view(),
        name="check-is-product",
    ),
]
