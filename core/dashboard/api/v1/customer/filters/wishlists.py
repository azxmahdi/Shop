import django_filters

from shop.models import WishlistProductModel


class WishlistFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="custom_search", label="جستجو")
    order_by = django_filters.OrderingFilter(
        fields=(("product__title", "product__title"),),
        field_labels={
            "product__title": "عنوان محصول",
        },
        label="مرتب‌سازی بر اساس",
    )

    class Meta:
        model = WishlistProductModel
        fields = []

    def custom_search(self, queryset, name, value):
        return queryset.filter(product__title__icontains=value)
