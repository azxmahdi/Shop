from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import UserType
from dashboard.api.v1.pagination import CustomPagination
from dashboard.api.v1.permissions import IsAdminOrSuperUser

from ..filters import UserFilter
from ..serializers import UserSerializer

User = get_user_model()


class UserListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def get_queryset(self):
        queryset = User.objects.all()

        if self.request.user.type == UserType.admin.value:
            queryset = queryset.filter(
                type=UserType.customer.value, is_superuser=False
            )

        return queryset


class UserDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    queryset = User.objects.all()

    def get_queryset(self):

        user = self.request.user
        if user.type == UserType.superuser.value:
            return User.objects.all()
        elif user.type == UserType.admin.value:
            return User.objects.filter(
                is_superuser=False, type=UserType.customer.value
            )
        return User.objects.none()

    def perform_destroy(self, instance):

        if instance.products.exists():
            raise ValidationError(
                {"detail": "حذف کاربر ناممکن: کاربر دارای محصولات فعال است"},
                code="protected_relation",
            )

        try:
            instance.delete()
        except ProtectedError as e:
            protected_objects = [
                obj._meta.verbose_name for obj in e.protected_objects
            ]
            raise ValidationError(
                {
                    "detail": "حذف ناموفق به دلیل وجود وابستگی‌های اجباری",
                    "protected_objects": protected_objects,
                }
            )

    def delete(self, request, *args, **kwargs):

        try:
            instance = self.get_object()
            self.check_object_permissions(request, instance)
            self.perform_destroy(instance)
            return Response(
                {"detail": "کاربر مورد نظر با موفقیت حذف شد"},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied:
            return Response(
                {"detail": "شما مجوز انجام این عمل را ندارید"},
                status=status.HTTP_403_FORBIDDEN,
            )


class UserUpdateAPI(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.type == UserType.superuser.value:
            queryset = User.objects.all()
            return queryset
        elif user.type == UserType.admin.value:
            queryset = User.objects.filter(
                type__in=[UserType.customer.value, UserType.admin.value],
                is_superuser=False,
            )
            return queryset
        return User.objects.none()
