from shop.models import ProductModel, ProductStatusType

def is_validate_quantity_product(cart, product_id):
    cart = cart._cart['items']
    if product_id in cart:
        quantity = cart[product_id]['quantity']
    else:
        quantity = 1
    product_obj = ProductModel.objects.get(id=product_id, status=ProductStatusType.publish.value)
    if product_id and product_obj:
        if product_obj.stock > quantity:
            return True
        return False
    return False
