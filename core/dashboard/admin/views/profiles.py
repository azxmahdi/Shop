from django.views.generic import FormView, UpdateView
from django.views.generic.edit import FormView
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from ..forms import AdminChangePasswordForm, AdminProfileEditForm
from ...permissions import HasAdminAccessPermission
from accounts.models import Profile




class AdminSecurityEditView(LoginRequiredMixin, HasAdminAccessPermission, FormView):
    template_name = 'dashboard/admin/profile/security-edit.html'
    form_class = AdminChangePasswordForm

    def form_valid(self, form):
        old_password = form.cleaned_data['old_password']
        new_password = form.cleaned_data['new_password']

        user = authenticate(self.request, email=self.request.user.email, password=old_password)
        if user is not None:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(self.request, user)  
            messages.success(self.request, _('رمز عبور با موفقیت تغییر یافت'))
        else:
            messages.error(self.request, _("پسورد قبلی شما اشتباه وارد شده است، لطفا تصحیح نمایید."))

        return redirect('dashboard:admin:security-edit')

    def form_invalid(self, form):
        messages.error(self.request, _("لطفا اطلاعات را به درستی وارد کنید."))
        return super().form_invalid(form)



class AdminProfileEditView(UpdateView):
    model = Profile
    form_class = AdminProfileEditForm
    template_name = 'dashboard/admin/profile/profile-edit.html' 
    success_url = reverse_lazy('dashboard:admin:profile-edit')
    

    def form_valid(self, form):
        # اگر کاربر دکمه "حذف کردن" را زده باشد
        if form.cleaned_data.get('delete_image'):
            form.instance.image = 'profile/default.png'  # تصویر پیش‌فرض
        messages.success(self.request, "بروز رسانی پروفایل با موفقیت انجام شد") 
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "بروز رسانی پروفایل با مشکل مواجه شد . لطفا مجدد تلاش کنید")
        return super().form_invalid(form)
        
    
    def get_object(self, queryset=None):
        return self.request.user.user_profile

    

