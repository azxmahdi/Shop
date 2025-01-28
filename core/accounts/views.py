
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, View, TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from itsdangerous import URLSafeTimedSerializer
from django.conf import settings
from django.contrib.auth.hashers import make_password

from django.contrib import messages
from django.shortcuts import redirect, render

User = get_user_model()

from .models import Profile
from .forms import SignInForm, SignUpForm, ResetPasswordForm, ChangePasswordTokenForm
from .tasks import send_email

User = get_user_model()

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

def generate_activation_token(email):
    return serializer.dumps(email, salt='email-activation-salt')

def verify_activation_token(token, expiration=60 * 60):
    try:
        email = serializer.loads(token, salt='email-activation-salt', max_age=expiration)
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
        email = str(email)

        user = authenticate(email=email, password=password)

        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:  
            messages.error(self.request, "This user does not exist.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class SignUpView(FormView):
    template_name = "accounts/sign_up.html"
    form_class = SignUpForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        first_name = form.cleaned_data["first_name"]
        last_name = form.cleaned_data["last_name"]
        image = form.cleaned_data["image"]
        password = form.cleaned_data["password"]
        confirm_password = form.cleaned_data["confirm_password"]

        if not User.objects.filter(email=email).exists():
            if password == confirm_password:
                user = User.objects.create_user(email=email, password=password)
                profile = Profile.objects.get(user=user)
                profile.first_name = first_name
                profile.last_name = last_name
                if image:
                    profile.image = image
                profile.save()
                user = authenticate(request=self.request, email=email, password=password)
                login(self.request, user)
                return redirect('accounts:verified_email')
            else:
                messages.error(
                    self.request,
                    "New password and confirm password do not match.",
                )
                return redirect('accounts:sign_up')
        else:
            messages.error(self.request, "This username already exists.")
            return redirect('accounts:sign_up')

    def form_invalid(self, form):
        messages.error(self.request, "The entered captcha does not match.")
        return super().form_invalid(form)


class LogoutView(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("website:index")
    

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

def generate_activation_token(email):
    return serializer.dumps(email, salt='email-activation-salt')

def verify_activation_token(token, expiration=60 * 60):
    try:
        email = serializer.loads(token, salt='email-activation-salt', max_age=expiration)
    except Exception:
        return None
    return email
    
class SendMailRestPassword(FormView):
    template_name = 'accounts/send_mail_reset_password.html'
    form_class = ResetPasswordForm
    success_url = reverse_lazy('website:index')

    def form_valid(self, form):
        email_to = form.cleaned_data["email"]
        token = generate_activation_token(email_to)
        url = reverse('accounts:reset_password', args=[token])
        full_url = self.request.build_absolute_uri(url)
        tpl_name = 'mail/reset_password.tpl'
        try:
            profile = Profile.objects.get(user__email=email_to)
        except Profile.DoesNotExist:
            messages.error(self.request, 'The email you entered does not exist')
            return redirect('accounts:send_mail_reset_password')
        context = {'name':profile.last_name, 'url':full_url}
        email = 'azxmahdi22@gmail.com'
        to = [email_to,]
        send_email.delay(tpl_name, context, email, to)

        messages.success(self.request,"Please check your email")
        return redirect('accounts:send_mail_reset_password')
    
    def form_invalid(self, form):
        return super().form_invalid(form) 
    
class RestPassword(View):
    def get(self, request, token):
        if not token:
            return render(request, 'accounts/change_password_token.html', {'error': 'Token not found'})

        email = verify_activation_token(token)

        if email is None:
            return render(request, 'accounts/change_password_token.html', {'error': 'The token is invalid or expired.'})

        form = ChangePasswordTokenForm()
        return render(request, 'accounts/change_password_token.html', {'form': form})

    def post(self, request, token):
        if not token:
            return render(request, 'accounts/change_password_token.html', {'error': 'Token not found'})

        email = verify_activation_token(token)

        if email is None:
            return render(request, 'accounts/change_password_token.html', {'error': 'The token is invalid or expired.'})

        form = ChangePasswordTokenForm(request.POST)

        if form.is_valid():
            new_password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match!")
                return render(request, 'accounts/change_password_token.html', {'form': form})

            user = User.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()

            return redirect('accounts:login')

        return render(request, 'accounts/change_password_token.html', {'form': form})


