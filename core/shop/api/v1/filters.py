import django_filters

from shop.models import CategoryFeature


class CategoryFeatureFilter(django_filters.FilterSet):
    category_id = django_filters.CharFilter(
        method="getting_features_based_on_category_id", label="Category ID"
    )
    is_required = django_filters.BooleanFilter(
        method="getting_the_required_features"
    )

    class Meta:
        model = CategoryFeature
        fields = []

    def getting_features_based_on_category_id(self, queryset, name, value):
        return queryset.filter(category__id=value)

    def getting_the_required_features(self, queryset, name, value):
        return queryset.filter(is_required=value)
