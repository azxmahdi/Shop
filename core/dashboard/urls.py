from django.urls import include, path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("home/", views.DashboardHomeView.as_view(), name="home"),
    path("admin/", include("dashboard.admin.urls"), name="admin"),
    path("customer/", include("dashboard.customer.urls"), name="customer"),
    path("api/v1/", include("dashboard.api.v1.urls"), name="api-v1"),
]
