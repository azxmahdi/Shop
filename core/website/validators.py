from django.core.exceptions import ValidationError
import re

def validate_phone_number(value):
    if not re.match(r'^\+989\d{9}$', value):
        raise ValidationError('شماره وارد شده نامعتبر است')
