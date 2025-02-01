from django import template

from ..models import ProductModel, ProductStatusType

register = template.Library()

@register.inclusion_tag('includes/latest-products.html')
def latest_products():
    queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value, stock__gt=0).order_by('-created_date')[:8]
    return {'latest_products':queryset}



@register.inclusion_tag('includes/similar-products.html')
def similar_products(product):
    categories = product.category.all()
    queryset = ProductModel.objects.exclude(id=product.id, status=ProductStatusType.publish.value, stock__gt=0, category__in=categories).order_by('-created_date').distinct()[:8]
    return {'similar_products':queryset}