from django.urls import include, path

from . import views

app_name = "order"

urlpatterns = [
    path("api/v1/", include("order.api.v1.urls"), name="api-v1"),
    path(
        "validate-coupon/",
        views.ValidateCouponView.as_view(),
        name="validate-coupon",
    ),
    path("checkout/", views.OrderCheckOutView.as_view(), name="checkout"),
    path("completed/", views.OrderCompletedView.as_view(), name="completed"),
    path("failed/", views.OrderFailedView.as_view(), name="failed"),
]
