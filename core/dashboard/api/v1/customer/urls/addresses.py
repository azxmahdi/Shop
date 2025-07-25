from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .. import views

router = DefaultRouter()
router.register("addresses", views.UserAddressViewSetAPI, basename="address")


urlpatterns = [path("", include(router.urls))]
