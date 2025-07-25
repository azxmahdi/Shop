from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from dashboard.api.v1.pagination import CustomPagination
from dashboard.api.v1.permissions import IsCustomer
from order.models import UserAddressModel

from ..serializers import UserAddressSerializer


class UserAddressViewSetAPI(ModelViewSet):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = UserAddressSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return UserAddressModel.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data["detail"] = "ایجاد آدرس با موفقیت انجام شد"
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data["detail"] = "ویرایش آدرس با موفقیت انجام شد"
        return response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "حذف آدرس با موفقیت انجام شد"},
            status=status.HTTP_204_NO_CONTENT,
        )
