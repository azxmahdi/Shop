from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dashboard.api.v1.pagination import CustomPagination
from dashboard.api.v1.permissions import IsCustomer
from shop.models import WishlistProductModel

from ..filters import WishlistFilter
from ..serializers import WishlistSerializer


class WishlistListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = WishlistSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = WishlistFilter

    def get_queryset(self):
        return WishlistProductModel.objects.filter(user=self.request.user)


class WishlistDeleteAPI(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = WishlistSerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        return WishlistProductModel.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "محصول با موفقیت از لیست حذف شد"},
            status=status.HTTP_204_NO_CONTENT,
        )
