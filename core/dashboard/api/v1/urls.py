from django.urls import include, path

app_name = "api-v1"

urlpatterns = [
    path("admin/", include("dashboard.api.v1.admin.urls"), name="admin"),
    path(
        "customer/", include("dashboard.api.v1.customer.urls"), name="customer"
    ),
]
