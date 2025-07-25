from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny

from website.models import ContactModel, NewsLetter, TeamMembers

from .filters import TeamMemberFilter
from .serializers import (
    ContactSerializer,
    NewsLetterSerializer,
    TeamMemberSerializer,
)


class TeamMemberListAPI(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TeamMemberSerializer
    queryset = TeamMembers.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = TeamMemberFilter


class ContactCreateAPI(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ContactSerializer
    queryset = ContactModel.objects.all()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data["detail"] = "همکاران ما به زودی با شما تماس خواهند گرفت"
        return response


class NewsletterCreateAPI(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = NewsLetterSerializer
    queryset = NewsLetter.objects.all()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data["detail"] = (
            "از ثبت نام شما ممنونم، اخبار جدید رو براتون ارسال می کنم"
        )
        return response
