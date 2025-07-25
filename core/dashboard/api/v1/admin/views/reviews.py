from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from dashboard.api.v1.pagination import CustomPagination
from dashboard.api.v1.permissions import IsAdminOrSuperUser
from review.models import ReviewModel, ReviewStatusType

from ..filters import ReviewFilter
from ..serializers import ReviewSerializer


class ReviewListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    queryset = ReviewModel.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReviewFilter
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data["status_types"] = ReviewStatusType.choices
        return response


class ReviewRetrieveUpdateAPI(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    queryset = ReviewModel.objects.all()
    serializer_class = ReviewSerializer

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data["detail"] = "تغییرات با موفقیت اعمال شد"
        return response
