from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms

from shop.models import ProductCategoryModel, ProductImageModel, ProductModel


class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = [
            "category",
            "title",
            "slug",
            "image",
            "description",
            "brief_description",
            "stock",
            "status",
            "price",
            "discount_percent",
        ]
        widgets = {
            "description": CKEditorUploadingWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs["class"] = "form-control"
        self.fields["slug"].widget.attrs["class"] = "form-control"
        self.fields["category"].widget.attrs["class"] = "form-control"
        self.fields["image"].widget.attrs["class"] = "form-control"
        self.fields["brief_description"].widget.attrs["class"] = "form-control"
        self.fields["description"].widget.attrs["id"] = "ckeditor"
        self.fields["stock"].widget.attrs["class"] = "form-control"
        self.fields["stock"].widget.attrs["type"] = "number"
        self.fields["status"].widget.attrs["class"] = "form-select"
        self.fields["price"].widget.attrs["class"] = "form-control"
        self.fields["discount_percent"].widget.attrs["class"] = "form-control"
        self.fields["category"].queryset = ProductCategoryModel.objects.filter(
            parent__isnull=False
        )


class ProductImageForm(forms.ModelForm):

    class Meta:
        model = ProductImageModel
        fields = [
            "file",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].widget.attrs["class"] = "form-control"


class ProductFeatureForm(forms.Form):
    def __init__(self, *args, **kwargs):
        product_id = kwargs.pop("product_id")
        super().__init__(*args, **kwargs)
        product = ProductModel.objects.get(id=product_id)
        all_features = product.category.get_all_features()

        for feature in all_features:
            attrs = {
                "class": (
                    "form-select"
                    if feature.options.exists()
                    else "form-control"
                ),
                "data-is-required": str(feature.is_required),
            }

            if feature.options.exists():
                self.fields[f"feature_{feature.id}"] = forms.ChoiceField(
                    choices=self._get_choices_with_empty(feature),
                    label=feature.name,
                    required=feature.is_required,
                    widget=forms.Select(attrs=attrs),
                )
            else:
                self.fields[f"feature_{feature.id}"] = forms.CharField(
                    label=feature.name,
                    required=feature.is_required,
                    widget=forms.TextInput(attrs=attrs),
                )

    def _get_choices_with_empty(self, feature):
        choices = [(opt.id, opt.value) for opt in feature.options.all()]
        if not feature.is_required:
            choices.insert(0, ("", "----"))
        return choices
