from django.urls import include, path

from . import views

app_name = "website"

urlpatterns = [
    path("api/v1/", include("website.api.v1.urls"), name="api-v1"),
    path("", views.IndexTemplateView.as_view(), name="index"),
    path("about/", views.AboutTemplateView.as_view(), name="about"),
    path("contact/", views.ContactTemplateView.as_view(), name="contact"),
    path("newsletter/", views.NewsletterView.as_view(), name="newsletter"),
]
