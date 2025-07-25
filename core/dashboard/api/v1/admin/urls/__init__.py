from django.urls import include, path

app_name = "admin"

urlpatterns = [
    path("", include("dashboard.api.v1.admin.urls.contacts"), name="contacts"),
    path("", include("dashboard.api.v1.admin.urls.coupons"), name="coupons"),
    path(
        "",
        include("dashboard.api.v1.admin.urls.newsletters"),
        name="newsletters",
    ),
    path("", include("dashboard.api.v1.admin.urls.orders"), name="orders"),
    path("", include("dashboard.api.v1.admin.urls.reviews"), name="reviews"),
    path("", include("dashboard.api.v1.admin.urls.users"), name="users"),
    path("", include("dashboard.api.v1.admin.urls.profiles"), name="profiles"),
    path("", include("dashboard.api.v1.admin.urls.products"), name="products"),
]
