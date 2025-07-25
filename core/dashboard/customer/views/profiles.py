from django.contrib import messages
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, UpdateView

from accounts.models import Profile

from ...permissions import HasCustomerAccessPermission
from ..forms import CustomerChangePasswordForm, CustomerProfileEditForm


class CustomerSecurityEditView(
    LoginRequiredMixin, HasCustomerAccessPermission, FormView
):
    template_name = "dashboard/customer/profile/security-edit.html"
    form_class = CustomerChangePasswordForm

    def form_valid(self, form):
        old_password = form.cleaned_data["old_password"]
        new_password = form.cleaned_data["new_password"]

        user = authenticate(
            self.request, email=self.request.user.email, password=old_password
        )
        if user is not None:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(self.request, user)
            messages.success(self.request, _("رمز عبور با موفقیت تغییر یافت"))
        else:
            messages.error(
                self.request,
                _("پسورد قبلی شما اشتباه وارد شده است، لطفا تصحیح نمایید."),
            )

        return redirect("dashboard:customer:security-edit")

    def form_invalid(self, form):
        messages.error(self.request, _("لطفا اطلاعات را به درستی وارد کنید."))
        return super().form_invalid(form)


class CustomerProfileEditView(
    LoginRequiredMixin, HasCustomerAccessPermission, UpdateView
):
    model = Profile
    form_class = CustomerProfileEditForm
    template_name = "dashboard/customer/profile/profile-edit.html"
    success_url = reverse_lazy("dashboard:customer:profile-edit")

    def form_valid(self, form):
        if form.cleaned_data.get("delete_image"):
            form.instance.image = "profile/default.png"
        messages.success(self.request, "بروز رسانی پروفایل با موفقیت انجام شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "بروز رسانی پروفایل با مشکل مواجه شد . لطفا مجدد تلاش کنید",
        )
        return super().form_invalid(form)

    def get_object(self, queryset=None):
        return self.request.user.user_profile
