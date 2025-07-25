import jwt
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.urls import reverse
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import Profile

from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    LoginSerializer,
    ProfileSerializer,
    RegistrationSerializer,
    ResendEmailConfirmSerializer,
)
from .tasks import send_email_task

User = get_user_model()


class RegistrationView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = serializer.save()
            token = self.get_tokens_for_user(user)
            url = reverse("accounts:api-v1:email-confirm", args=[token])
            full_url = request.build_absolute_uri(url)
            from_email = "your_email@example.com"
            recipient_list = [email]

            send_email_task.delay(
                template="mail/send-mail-confirm.tpl",
                data={"url": full_url},
                from_email=from_email,
                to=recipient_list,
            )

            return Response(
                {"detail": "لطفا ایمیل خود را چک کنید"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class EmailConfirmView(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    def get(self, request, token, *args, **kwargs):
        try:
            decoded_token = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"]
            )

        except jwt.ExpiredSignatureError:
            return Response({"detail": "این توکن منقضی شده است."})
        except jwt.InvalidTokenError:
            return Response({"detail": "توکن اشتباه است."})
        user_id = decoded_token.get("user_id")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "کاربر یافت نشد."})

        user.is_verified = True
        user.save()
        return Response({"detail": "اکانت شما با موفقیت فعال شد."})


class ResendEmailConfirmView(generics.GenericAPIView):
    permission_classes = [
        permissions.AllowAny,
    ]
    serializer_class = ResendEmailConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data["email"])

            token = self.get_tokens_for_user(user)
            url = reverse("accounts:api-v1:email-confirm", args=[token])
            full_url = request.build_absolute_uri(url)
            from_email = "your_email@example.com"
            recipient_list = [serializer.validated_data["email"]]

            send_email_task.delay(
                template="mail/send-mail-confirm.tpl",
                data={"url": full_url},
                from_email=from_email,
                to=recipient_list,
            )

            return Response(
                {"detail": "لطفا ایمیل خود را چک کنید"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class TokenLoginView(generics.GenericAPIView):
    permission_classes = [
        permissions.AllowAny,
    ]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = authenticate(email=email, password=password)
            if user is not None:
                if user.is_verified:
                    token, created = Token.objects.get_or_create(user=user)
                    return Response(
                        {"token": token.key, "email": email},
                        status=status.HTTP_200_OK,
                    )

                else:
                    return Response(
                        {"detail": "اکانت شما فعال نیست."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"detail": "کاربری با این مشخصات وجود ندارد."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenLogoutView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response(
                {"detail": "با موفقیت خارج شدید"}, status=status.HTTP_200_OK
            )
        except (AttributeError, Token.DoesNotExist):
            return Response(
                {"detail": "توکن وجود ندارد"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.object.set_password(serializer.validated_data["new_password"])
        self.object.save()
        return Response(
            {"detail": "پسورد با موفقیت تغییر کرد."}, status=status.HTTP_200_OK
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_object(self):
        return Profile.objects.get(user=self.request.user)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
