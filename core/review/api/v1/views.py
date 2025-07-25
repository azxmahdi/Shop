from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from review.models import ReviewModel

from .serializers import ReviewSerializer


class SubmitReviewAPI(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return ReviewModel.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data["detail"] = (
            "دیدگاه شما با موفقیت ثبت شد و پس از بررسی نمایش داده خواهد شد"
        )
        return response
