from django.urls import path

from .. import views

urlpatterns = [
    path("order/list/", views.OrderListAPI.as_view(), name="order-list"),
    path(
        "order/detail/<int:pk>/",
        views.OrderDetailAPI.as_view(),
        name="order-detail",
    ),
    path(
        "order/invoice/<int:pk>/",
        views.OrderInvoiceAPI.as_view(),
        name="order-invoice",
    ),
]
