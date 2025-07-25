from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from dashboard.api.v1.pagination import CustomPagination
from dashboard.api.v1.permissions import IsAdminOrSuperUser
from order.models import OrderModel, OrderStatusType

from ..filters import OrderFilter
from ..serializers import OrderDetailSerializer, OrderListSerializer


class OrderListAPI(generics.ListAPIView):
    queryset = OrderModel.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_class = OrderListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data["status_types"] = OrderStatusType.choices
        return response


class OrderDetailAPI(generics.RetrieveAPIView):
    queryset = OrderModel.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_class = OrderDetailSerializer


class OrderInvoiceAPI(generics.RetrieveAPIView):
    queryset = OrderModel.objects.filter(status=OrderStatusType.success.value)
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_class = OrderDetailSerializer
