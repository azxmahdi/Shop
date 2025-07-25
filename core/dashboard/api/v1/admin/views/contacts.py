from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from dashboard.api.v1.pagination import CustomPagination
from dashboard.api.v1.permissions import IsAdminOrSuperUser
from website.models import ContactModel

from ..filters import ContactFilter
from ..serializers import ContactDetailSerializer, ContactSerializer


class ContactListAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ContactFilter
    pagination_class = CustomPagination

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ContactModel.objects.none()
        return ContactModel.objects.all()

    def get(self, request):
        queryset = ContactModel.objects.all().order_by("-created_date")

        filtered_queryset = self.filter_queryset(queryset)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(filtered_queryset, request)

        serializer = ContactSerializer(
            page, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)

    def filter_queryset(self, queryset):
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset


class ContactDetailAPI(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_class = ContactDetailSerializer
    queryset = ContactModel.objects.all()
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    def get_object(self):
        try:
            obj = ContactModel.objects.get(
                pk=self.kwargs[self.lookup_url_kwarg]
            )
            if not obj.is_seen:
                obj.is_seen = True
                obj.save(update_fields=["is_seen"])
            return obj
        except ContactModel.DoesNotExist:
            raise NotFound("Contact not found")
