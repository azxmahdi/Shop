import django_filters

from review.models import ReviewModel, ReviewStatusType


class ReviewFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="custom_search", label="جستجو")
    order_by = django_filters.OrderingFilter(
        fields=(
            ("created_date", "created_date"),
            ("updated_date", "updated_date"),
            ("rate", "rate"),
        ),
        field_labels={
            "created_date": "تاریخ ایجاد",
            "updated_date": "تاریخ به‌روزرسانی",
            "rate": "امتیاز",
        },
        label="مرتب‌سازی بر اساس",
    )
    status = django_filters.ChoiceFilter(
        choices=ReviewStatusType.choices, label="وضعیت کامنت"
    )

    class Meta:
        model = ReviewModel
        fields = []

    def custom_search(self, queryset, name, value):
        return queryset.filter(product__title__icontains=value)
