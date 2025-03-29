from django import template

from ..models import ProductModel, ProductStatusType, WishlistProductModel

register = template.Library()


@register.inclusion_tag("includes/latest-products.html",takes_context=True)
def latest_products(context):
    request = context.get("request")
    latest_products = ProductModel.objects.filter(
        status=ProductStatusType.publish.value).distinct().order_by("-created_date")[:8]
    wishlist_items = WishlistProductModel.objects.filter(user=request.user).values_list("product__id",flat=True) if request.user.is_authenticated else []
    return {"latest_products": latest_products,"request":request,"wishlist_items":wishlist_items}




@register.inclusion_tag("includes/similar-products.html",takes_context=True)
def similar_products(context,product):
    request = context.get("request")
    product_categories= product.category.all()
    similar_prodcuts = ProductModel.objects.filter(
        status=ProductStatusType.publish.value,category__in=product_categories).distinct().exclude(id=product.id).order_by("-created_date")[:4]
    wishlist_items =  WishlistProductModel.objects.filter(user=request.user).values_list("product__id",flat=True) if request.user.is_authenticated else []
    return {"similar_prodcuts": similar_prodcuts,"request":request,"wishlist_items":wishlist_items}




@register.inclusion_tag('includes/category_node.html')
def render_category(node):
    return {'node': node}


@register.filter
def get(dictionary, key):
    return dictionary.get(key, '')

@register.filter
def getlist(dictionary, key):
    return dictionary.getlist(key, [])

@register.filter(name='startswith')
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])

@register.simple_tag
def is_filter_active(feature_id, option_value, current_filters):
    param_name = f"feature_{feature_id}"
    selected_values = current_filters.getlist(param_name, [])
    return str(option_value) in selected_values
