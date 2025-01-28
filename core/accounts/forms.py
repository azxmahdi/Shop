from django import forms


class SignUpForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=225)
    last_name = forms.CharField(max_length=225)
    image = forms.ImageField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)



class SignInForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class ResetPasswordForm(forms.Form):
    email = forms.EmailField()

class ChangePasswordTokenForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

