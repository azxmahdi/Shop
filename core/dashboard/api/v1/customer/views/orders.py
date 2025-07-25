from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from dashboard.api.v1.pagination import CustomPagination
from dashboard.api.v1.permissions import IsCustomer
from order.models import OrderModel, OrderStatusType

from ..filters import OrderFilter
from ..serializers import OrderDetailSerializer, OrderListSerializer


class OrderListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = OrderListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter
    pagination_class = CustomPagination

    def get_queryset(self):
        return OrderModel.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data["status_types"] = OrderStatusType.choices
        return response


class OrderDetailAPI(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return OrderModel.objects.filter(user=self.request.user)


class OrderInvoiceAPI(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return OrderModel.objects.filter(
            user=self.request.user, status=OrderStatusType.success.value
        )
