from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, View
from itsdangerous import URLSafeTimedSerializer

from .forms import (
    ChangePasswordTokenForm,
    ResetPasswordForm,
    SignInForm,
    SignUpForm,
)
from .models import Profile
from .tasks import send_email

User = get_user_model()

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


def generate_activation_token(email):
    return serializer.dumps(email, salt="email-activation-salt")


def verify_activation_token(token, expiration=60 * 60):
    try:
        email = serializer.loads(
            token, salt="email-activation-salt", max_age=expiration
        )
    except Exception:
        return None
    return email


class LoginView(FormView):
    template_name = "accounts/login.html"
    form_class = SignInForm
    success_url = reverse_lazy("website:index")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user is not None and user.check_password(password):
            if user.is_active:
                login(self.request, user)
                return super().form_valid(form)
            else:
                messages.error(
                    self.request,
                    "حساب کاربری شما غیر فعال شده است. لطفا با پشتیبانی تماس بگیرید.",
                )
                return redirect("accounts:login")
        else:
            messages.error(self.request, "اطلاعات وارد شده درست نیست")
            return self.form_invalid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class SignUpView(FormView):
    template_name = "accounts/sign-up.html"
    form_class = SignUpForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        confirm_password = form.cleaned_data["confirm_password"]

        if not User.objects.filter(email=email).exists():
            if password == confirm_password:
                user = User.objects.create_user(email=email, password=password)
                messages.success(
                    self.request,
                    "ثبت نام موفقیت آمیز بود. برای ورود لطفا اطلاعات خود را وارد کنید.",
                )
                return redirect("accounts:login")
            else:
                messages.error(
                    self.request,
                    "رمز عبور جدید و تأییدیه آن مطابقت ندارند.",
                )
                return redirect("accounts:sign-up")
        else:
            messages.error(self.request, "کاربری با ایمیل وارد شده وجود دارد.")
            return redirect("accounts:sign-up")

    def form_invalid(self, form):
        return super().form_invalid(form)


class LogoutView(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("website:index")


serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


def generate_activation_token(email):
    return serializer.dumps(email, salt="email-activation-salt")


def verify_activation_token(token, expiration=60 * 60):
    try:
        email = serializer.loads(
            token, salt="email-activation-salt", max_age=expiration
        )
    except Exception:
        return None
    return email


class SendMailRestPasswordFormView(FormView):
    template_name = "accounts/send-mail-reset-password.html"
    form_class = ResetPasswordForm
    success_url = reverse_lazy("website:index")

    def form_valid(self, form):
        email_to = form.cleaned_data["email"]
        token = generate_activation_token(email_to)
        url = reverse("accounts:reset-password", args=[token])
        full_url = self.request.build_absolute_uri(url)
        tpl_name = "mail/reset-password.tpl"
        try:
            profile = Profile.objects.get(user__email=email_to)
        except Profile.DoesNotExist:
            messages.error(self.request, "کاربری با این ایمیل وجود ندارد")
            return redirect("accounts:send-mail-reset-password")
        if not profile.user.is_active:
            messages.error(
                self.request,
                "حساب کاربری شما غیر فعال شده است. لطفا با پشتیبانی تماس بگیرید.",
            )
            return redirect("accounts:send-mail-reset-password")
        context = {"name": profile.last_name, "url": full_url}
        email = "azxmahdi22@gmail.com"
        to = [
            email_to,
        ]
        send_email.delay(tpl_name, context, email, to)

        messages.success(self.request, "لطفا ایمیل خود را چک کنید")
        return redirect("accounts:send-mail-reset-password")

    def form_invalid(self, form):
        return super().form_invalid(form)


class RestPasswordView(View):
    def get(self, request, token):
        if not token:
            return render(
                request,
                "accounts/change_password_token.html",
                {"error": "توکن پیدا نشد"},
            )

        email = verify_activation_token(token)

        if email is None:
            return render(
                request,
                "accounts/change_password_token.html",
                {
                    "error": "زمان تغییر پسورد به پایان رسیده است. لطفا مجددا ایمیل بازنشانی پسورد را ارسال کنید"
                },
            )

        form = ChangePasswordTokenForm()
        return render(
            request, "accounts/change_password_token.html", {"form": form}
        )

    def post(self, request, token):
        if not token:
            return render(
                request,
                "accounts/change_password_token.html",
                {"error": "توکن پیدا نشد"},
            )

        email = verify_activation_token(token)

        if email is None:
            return render(
                request,
                "accounts/change_password_token.html",
                {
                    "error": "زمان تغییر پسورد به پایان رسیده است. لطفا مجددا ایمیل بازنشانی پسورد را ارسال کنید"
                },
            )

        form = ChangePasswordTokenForm(request.POST)

        if form.is_valid():
            new_password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]

            if new_password != confirm_password:
                messages.error(
                    request, "رمز عبور جدید و تأییدیه آن مطابقت ندارند."
                )
                return render(
                    request,
                    "accounts/change_password_token.html",
                    {"form": form},
                )

            user = User.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()

            return redirect("accounts:login")

        else:
            return render(
                request, "accounts/change_password_token.html", {"form": form}
            )
