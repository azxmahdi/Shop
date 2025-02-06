from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("session/add-product/",views.SessionAddProductView.as_view(),name="session-add-product"),
    path("session/remove-product/",views.SessionRemoveProductView.as_view(),name="session-remove-product"),
    path("session/update-product-quantity/",views.SessionUpdateProductQuantityView.as_view(),name="session-update-product-quantity"),
    path("session/check-is-product/",views.CheckIsProduct.as_view(),name="session-check-is-product"),
    path("session/update-product-quantity-detail/",views.SessionUpdateProductQuantityDetailView.as_view(),name="session-update-product-quantity-detail"),

    path("summary/",views.CartSummaryView.as_view(),name="cart-summary"),


]