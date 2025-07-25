from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dashboard.api.v1.pagination import CustomPagination
from dashboard.api.v1.permissions import IsAdminOrSuperUser
from website.models import NewsLetter

from ..filters import NewsletterFilter
from ..serializers import NewsLetterSerializer


class NewsletterListAPI(generics.ListAPIView):
    queryset = NewsLetter.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_class = NewsLetterSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = NewsletterFilter
    pagination_class = CustomPagination


class NewsletterDeleteAPI(generics.DestroyAPIView):
    queryset = NewsLetter.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_class = NewsLetterSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "عضو مورد نظر با موفقیت حذف شد"},
            status=status.HTTP_204_NO_CONTENT,
        )
