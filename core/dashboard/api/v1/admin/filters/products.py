import django_filters
from django.db.models import Q

from shop.models import ProductCategoryModel, ProductModel, ProductStatusType


class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="custom_search", label="جستجو")

    category = django_filters.ModelChoiceFilter(
        field_name="category__id",
        queryset=ProductCategoryModel.objects.all(),
        label="دسته‌بندی",
    )

    min_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="gte", label="حداقل قیمت"
    )

    max_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="lte", label="حداکثر قیمت"
    )

    status = django_filters.ChoiceFilter(
        choices=ProductStatusType.choices, label="وضعیت محصول"
    )

    order_by = django_filters.OrderingFilter(
        fields=(
            ("created_date", "created_date"),
            ("updated_date", "updated_date"),
            ("price", "price"),
            ("stock", "stock"),
        ),
        field_labels={
            "created_date": "تاریخ ایجاد",
            "updated_date": "تاریخ به‌روزرسانی",
            "price": "قیمت",
            "stock": "موجودی",
        },
        label="مرتب‌سازی بر اساس",
    )

    class Meta:
        model = ProductModel
        fields = []

    def custom_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value)
        )
