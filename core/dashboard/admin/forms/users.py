from django import forms
from django.contrib.auth import get_user_model

from accounts.models import UserType

User = get_user_model()


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "email",
            "type",
            "is_active",
            "is_verified",
        ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control mx-3 text-center mb-3",
                "readonly": "readonly",
            }
        )

        if (
            not self.request.user.is_superuser
            or self.request.user.type != UserType.superuser.value
        ):
            del self.fields["type"]
        else:
            self.fields["type"].widget.attrs["class"] = "form-select mb-3"
