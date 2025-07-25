import django_filters

from order.models import CouponModel


class CouponFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="custom_search", label="جستجو")
    order_by = django_filters.OrderingFilter(
        fields=(
            ("created_date", "created_date"),
            ("updated_date", "updated_date"),
            ("expiration_date", "expiration_date"),
            ("discount_percent", "discount_percent"),
            ("max_limit_usage", "max_limit_usage"),
        ),
        field_labels={
            "created_date": "تاریخ ایجاد",
            "updated_date": "تاریخ به‌روزرسانی",
            "expiration_date": "تاریخ انقضا",
            "discount_percent": "درصد تخفیف",
            "max_limit_usage": "حداکثر محدودیت استفاده",
        },
        label="مرتب‌سازی بر اساس",
    )

    class Meta:
        model = CouponModel
        fields = []

    def custom_search(self, queryset, name, value):
        return queryset.filter(code__icontains=value)
