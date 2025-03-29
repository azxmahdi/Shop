from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from shop.models import ProductModel, ProductImageModel, ProductCategoryModel



class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = [
            'category', 
            'title', 
            'slug', 
            'image', 
            'description', 
            'brief_description', 
            'stock', 
            'status', 
            'price',
            'discount_percent',
        ]
        widgets = {
            'description': CKEditorUploadingWidget(), 
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['slug'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-control'
        self.fields['image'].widget.attrs['class'] = 'form-control'
        self.fields['brief_description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['id'] = 'ckeditor'
        self.fields['stock'].widget.attrs['class'] = 'form-control'
        self.fields['stock'].widget.attrs['type'] = 'number'
        self.fields['status'].widget.attrs['class'] = 'form-select'
        self.fields['price'].widget.attrs['class'] = 'form-control'
        self.fields['discount_percent'].widget.attrs['class'] = 'form-control'
        self.fields['category'].queryset = ProductCategoryModel.objects.filter(parent__isnull=False)


class ProductImageForm(forms.ModelForm):


    class Meta:
        model = ProductImageModel
        fields = [
            "file",
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['class'] = 'form-control'
        self.fields['file'].widget.attrs['accept'] = 'image/png, image/jpg, image/jpeg'




class ProductFeatureForm(forms.Form):
    def __init__(self, *args, **kwargs):
        product_id = kwargs.pop('product_id')
        super().__init__(*args, **kwargs)
        product = ProductModel.objects.get(id=product_id)
        all_features = product.category.get_all_features()

        for feature in all_features:
            # افزودن داده به ویجت
            attrs = {
                'class': 'form-select' if feature.options.exists() else 'form-control',
                'data-is-required': str(feature.is_required)  # افزودن ویژگی جدید
            }

            if feature.options.exists():
                self.fields[f'feature_{feature.id}'] = forms.ChoiceField(
                    choices=self._get_choices_with_empty(feature),
                    label=feature.name,
                    required=feature.is_required,
                    widget=forms.Select(attrs=attrs)  # انتقال attrs
                )
            else:
                self.fields[f'feature_{feature.id}'] = forms.CharField(
                    label=feature.name,
                    required=feature.is_required,
                    widget=forms.TextInput(attrs=attrs)  # انتقال attrs
                )

    def _get_choices_with_empty(self, feature):
        """اضافه کردن گزینه خالی برای ویژگی‌های غیراجباری"""
        choices = [(opt.id, opt.value) for opt in feature.options.all()]
        if not feature.is_required:
            choices.insert(0, ('', '----'))  # گزینه خالی برای ویژگی غیراجباری
        return choices
