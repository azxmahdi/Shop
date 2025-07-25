from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dashboard.api.v1.pagination import CustomPagination
from dashboard.api.v1.permissions import IsAdminOrSuperUser
from order.models import CouponModel

from ..filters import CouponFilter
from ..serializers import CouponSerializer


class CouponViewSetAPI(viewsets.ModelViewSet):
    queryset = CouponModel.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_class = CouponSerializer
    lookup_field = "pk"
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = CouponFilter

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "حذف کد تخفیف با موفقیت انجام شد"},
            status=status.HTTP_204_NO_CONTENT,
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data["detail"] = "ویرایش کد تخفیف با موفقیت انجام شد"
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data["detail"] = "ایجاد کد تخفیف با موفقیت انجام شد"
        return response
