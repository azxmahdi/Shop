from django.urls import include, path

app_name = "customer"


urlpatterns = [
    path(
        "",
        include("dashboard.api.v1.customer.urls.addresses"),
        name="addresses",
    ),
    path("", include("dashboard.api.v1.customer.urls.orders"), name="orders"),
    path(
        "", include("dashboard.api.v1.customer.urls.profiles"), name="profiles"
    ),
    path(
        "",
        include("dashboard.api.v1.customer.urls.wishlists"),
        name="wishlists",
    ),
]
