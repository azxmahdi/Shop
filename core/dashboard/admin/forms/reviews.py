from django import forms
from django.core.exceptions import ValidationError

from review.models import ReviewModel


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewModel
        fields = ["description", "rate", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "rate": forms.NumberInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ["description", "rate"]:
            self.fields[field_name].widget.attrs.update(
                {"readonly": True, "class": "form-control"}
            )
        self.fields["status"].widget.attrs["class"] = "form-select"
        readonly_fields = ["description", "rate"]
        for field in readonly_fields:
            self.fields[field].widget.attrs["readonly"] = True

    def clean(self):
        cleaned_data = super().clean()

        if not self.instance:
            return cleaned_data

        immutable_fields = ["description", "rate"]

        for field in immutable_fields:
            if field in self.changed_data:
                current_value = getattr(self.instance, field)
                submitted_value = cleaned_data.get(field)

                if current_value != submitted_value:
                    raise ValidationError(
                        {
                            field: f"تغییر این فیلد مجاز نیست. مقدار فعلی: {current_value}"
                        }
                    )
        return cleaned_data
