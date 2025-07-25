import django_filters
from django.db.models import Q

from website.models import ContactModel


class ContactFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="custom_search", label="جستجو")
    order_by = django_filters.OrderingFilter(
        fields=(
            ("created_date", "created_date"),
            ("updated_date", "updated_date"),
        ),
        field_labels={
            "created_date": "تاریخ ایجاد",
            "updated_date": "تاریخ به‌روزرسانی",
        },
        label="مرتب‌سازی بر اساس",
    )

    class Meta:
        model = ContactModel
        fields = []

    def custom_search(self, queryset, name, value):
        return queryset.filter(
            Q(email__icontains=value)
            | Q(subject__icontains=value)
            | Q(content__icontains=value)
            | Q(phone_number__icontains=value)
        )
