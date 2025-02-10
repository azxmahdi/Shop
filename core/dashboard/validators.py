from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

class ChangePasswordValidator:
    """
    اعتبارسنجی که بررسی می‌کند رمز عبور شامل حداقل یک حرف بزرگ، یک حرف کوچک، یک عدد و یک نماد باشد.
    """
    status = True
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            self.status = False
        if not re.search(r'[a-z]', password):
            self.status = False
        if not re.search(r'[0-9]', password):
            self.status = False
        if not re.search(r'[^A-Za-z0-9]', password):
            self.status = False

        if not self.status:
            raise ValidationError (_(
            "رمز عبور شما باید حداقل شامل یک حرف بزرگ، یک حرف کوچک، یک عدد و یک نماد یا نویسه فضای خالی باشد."), 
            code="Not valid."
            )

    def get_help_text(self):
        return _(
            "رمز عبور شما باید حداقل شامل یک حرف بزرگ، یک حرف کوچک، یک عدد و یک نماد یا نویسه فضای خالی باشد."
        )