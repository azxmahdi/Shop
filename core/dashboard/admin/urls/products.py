from django.urls import path
from .. import views


urlpatterns = [
    path("product/list/",views.AdminProductListView.as_view(),name="product-list"),
    path("product/create/",views.AdminProductCreateView.as_view(),name="product-create"),
    path("product/<int:pk>/edit/",views.AdminProductEditView.as_view(),name="product-edit"),
    path("product/<int:pk>/delete/",views.AdminProductDeleteView.as_view(),name="product-delete"),
    path("product/<int:pk>/add-image/",views.AdminProductAddImageView.as_view(),name="product-add-image"),
    path("product/<int:pk>/image/<int:image_id>/remove/",views.AdminProductRemoveImageView.as_view(),name="product-remove-image"),


    path("product/<int:product_id>/add-features/<str:status>/",views.AdminAddProductFeatureFormView.as_view(),name="add-product-feature"),
    path("product/<int:product_id>/edit-features/",views.AdminEditProductFeatureFormView.as_view(),name="edit-product-feature"),
]
