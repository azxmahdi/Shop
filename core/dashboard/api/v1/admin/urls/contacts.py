from django.urls import path

from dashboard.api.v1.admin import views

urlpatterns = [
    path("contact/list/", views.ContactListAPI.as_view(), name="contact-list"),
    path(
        "contact/detail/<int:pk>/",
        views.ContactDetailAPI.as_view(),
        name="contact-detail",
    ),
]
