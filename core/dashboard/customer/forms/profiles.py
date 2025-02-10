from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ...validators import ChangePasswordValidator
from accounts.models import Profile



class CustomerChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs['class'] = 'form-control text-center'
        self.fields['new_password'].widget.attrs['class'] = 'form-control text-center'
        self.fields['confirm_password'].widget.attrs['class'] = 'form-control text-center'
        self.fields['old_password'].widget.attrs['placeholder'] = "پسورد قبلی خود را وارد نمایید"
        self.fields['new_password'].widget.attrs['placeholder'] = "پسورد جایگزین خود را وارد نمایید"
        self.fields['confirm_password'].widget.attrs['placeholder'] = "پسورد جایگزین خود را مجدد وارد نمایید"

        self.fields['new_password'].validators.append(ChangePasswordValidator().validate)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError(
                _("رمز عبور جدید و تأییدیه آن مطابقت ندارند."),
                code='password_mismatch',
            )

        return cleaned_data
    


class CustomerProfileEditForm(forms.ModelForm):
    delete_image = forms.BooleanField(
        required=False,  # اختیاری است
        widget=forms.HiddenInput(),  # مخفی است
        initial=False,  # مقدار پیش‌فرض
    )

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'phone_number', 'image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام خانوادگی'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره تلفن'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['placeholder'] = 'نام خود را وارد نمایید'
        self.fields['last_name'].widget.attrs['class'] = 'form-control '
        self.fields['last_name'].widget.attrs['placeholder'] = 'نام خانوادگی را وارد نمایید'
        self.fields['phone_number'].widget.attrs['class'] = 'form-control text-center'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'شماره همراه را وارد نمایید'
        self.fields['image'].widget.attrs['class'] = 'form-attachment-btn-label'