from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Profile
from dashboard.api.v1.permissions import IsAdminOrSuperUser

from ..serializers import ProfileSerializer, SecuritySerializer

User = get_user_model()


class SecurityEditAPI(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    queryset = User.objects.all()
    serializer_class = SecuritySerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(self.object, data=request.data)

        serializer.is_valid(raise_exception=True)

        self.object.set_password(serializer.validated_data["new_password"])
        self.object.save()

        return Response(
            {"detail": "رمز عبور شما با موفقیت تغییر یافت"},
            status=status.HTTP_200_OK,
        )


class ProfileEditAPI(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self):
        return self.queryset.get(user=self.request.user.id)
