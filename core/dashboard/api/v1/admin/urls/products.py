from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .. import views

router = DefaultRouter()
router.register(r"products", views.ProductViewSet, basename="product")
router.register(
    r"categories", views.ProductCategoryViewSet, basename="category"
)
router.register(
    r"categories/(?P<category_id>\d+)/features",
    views.CategoryFeatureViewSet,
    basename="category-feature",
)

urlpatterns = [
    path("", include(router.urls)),
]
