from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dashboard.api.v1.pagination import CustomPagination
from dashboard.api.v1.permissions import IsAdminOrSuperUser
from shop.models import (
    CategoryFeature,
    ProductCategoryModel,
    ProductFeature,
    ProductImageModel,
    ProductModel,
)

from ..filters import ProductFilter
from ..serializers import (
    CategoryFeatureSerializer,
    ProductCategorySerializer,
    ProductFeatureSerializer,
    ProductSerializer,
)


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data["detail"] = "ایجاد محصول با موفقیت انجام شد"
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data["detail"] = "ویرایش محصول با موفقیت انجام شد"
        return response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "حذف محصول با موفقیت انجام شد"},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=True, methods=["post"])
    def add_image(self, request, pk=None):
        product = self.get_object()
        image = request.FILES.get("file")

        if not image:
            return Response(
                {"error": "No image provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ProductImageModel.objects.create(product=product, file=image)
        print(ProductImageModel.objects.filter(product=product))
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"])
    def remove_image(self, request, pk=None):
        product = self.get_object()
        image_id = request.data.get("image_id")

        if not image_id:
            return Response(
                {"error": "image_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        image = get_object_or_404(
            ProductImageModel, id=image_id, product=product
        )
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def set_features(self, request, pk=None):
        product = self.get_object()
        serializer = ProductFeatureSerializer(data=request.data, many=True)

        if serializer.is_valid():
            ProductFeature.objects.filter(product=product).delete()

            for feature_data in serializer.validated_data:
                ProductFeature.objects.create(product=product, **feature_data)

            if request.data.get("status"):
                product.status = request.data["status"]
                product.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    queryset = ProductCategoryModel.objects.all()
    serializer_class = ProductCategorySerializer


class CategoryFeatureViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_class = CategoryFeatureSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return CategoryFeature.objects.none()

        category_id = self.kwargs["category_id"]
        category = get_object_or_404(ProductCategoryModel, id=category_id)
        return category.get_all_features()
