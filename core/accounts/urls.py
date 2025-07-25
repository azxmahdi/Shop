from django.urls import include, path

from . import views

app_name = "accounts"

urlpatterns = [
    path("api/v1/", include("accounts.api.v1.urls"), name="api-v1"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("sign-up/", views.SignUpView.as_view(), name="sign-up"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "reset-password/<str:token>/",
        views.RestPasswordView.as_view(),
        name="reset-password",
    ),
    path(
        "send-mail/reset-password/",
        views.SendMailRestPasswordFormView.as_view(),
        name="send-mail-reset-password",
    ),
]
