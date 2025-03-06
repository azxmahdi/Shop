from django.core.exceptions import ValidationError
import re
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    if not re.match(r'^09\d{9}$', value):
        raise ValidationError('شماره وارد شده نامعتبر است')
    


class PasswordValidator:
    """
    رمز عبور شما باید حداقل ۸ کاراکتر باشد و شامل یک حرف بزرگ، یک حرف کوچک، یک عدد و یک نماد باشد. 
    """
    def validate(self, password, user=None):
        errors = []

        if len(password) < 8:
            errors.append("حداقل ۸ کاراکتر لازم است.")
        if not re.search(r'[A-Z]', password):
            errors.append("حداقل یک حرف بزرگ انگلیسی نیاز است.")
        if not re.search(r'[a-z]', password):
            errors.append("حداقل یک حرف کوچک انگلیسی نیاز است.")
        if not re.search(r'[0-9]', password):
            errors.append("حداقل یک عدد نیاز است.")
        if not re.search(r'[^A-Za-z0-9]', password):
            errors.append("حداقل یک نماد خاص نیاز است.")

        if errors:
            raise ValidationError(errors)
    def get_help_text(self):
        return _("رمز عبور باید حداقل ۸ کاراکتر و شامل حروف بزرگ، کوچک، عدد و نماد باشد.")