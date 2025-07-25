from django.urls import path

from . import views

app_name = "api-v1"

urlpatterns = [
    path("checkout/", views.OrderCheckOutAPI.as_view(), name="checkout"),
    path(
        "validate-coupon/",
        views.ValidateCouponAPI.as_view(),
        name="validate-coupon",
    ),
]
