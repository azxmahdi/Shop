import django_filters
from django.db.models import Q

from order.models import OrderModel, OrderStatusType


class OrderFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="custom_search", label="جستجو")
    order_by = django_filters.OrderingFilter(
        fields=(
            ("created_date", "created_date"),
            ("updated_date", "updated_date"),
            ("total_price", "total_price"),
        ),
        field_labels={
            "created_date": "تاریخ ایجاد",
            "updated_date": "تاریخ به‌روزرسانی",
            "price": "قیمت کل",
        },
        label="مرتب‌سازی بر اساس",
    )
    status = django_filters.ChoiceFilter(
        choices=OrderStatusType.choices, label="وضعیت سفارش"
    )

    class Meta:
        model = OrderModel
        fields = []

    def custom_search(self, queryset, name, value):
        return queryset.filter(
            Q(user__user_profile__first_name__icontains=value)
            | Q(user__user_profile__last_name__icontains=value)
        )
