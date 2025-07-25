import django_filters

from website.models import NewsLetter


class NewsletterFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="custom_search", label="جستجو")
    order_by = django_filters.OrderingFilter(
        fields=(
            ("created_date", "created_date"),
            ("updated_date", "updated_date"),
            ("email", "email"),
        ),
        field_labels={
            "created_date": "تاریخ ایجاد",
            "updated_date": "تاریخ به‌روزرسانی",
            "email": "ایمیل",
        },
        label="مرتب‌سازی بر اساس",
    )

    class Meta:
        model = NewsLetter
        fields = []

    def custom_search(self, queryset, name, value):
        return queryset.filter(email__icontains=value)
