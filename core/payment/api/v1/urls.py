from django.urls import path

from . import views

app_name = "api-v1"


urlpatterns = [
    path("verify", views.PaymentVerifyAPI.as_view(), name="verify"),
]
