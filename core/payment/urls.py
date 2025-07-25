from django.urls import include, path

from . import views

app_name = "payment"

urlpatterns = [
    path("api/v1/", include("payment.api.v1.urls"), name="api-v1"),
    path("verify", views.PaymentVerifyView.as_view(), name="verify"),
]
