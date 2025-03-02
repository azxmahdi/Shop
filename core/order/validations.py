from cart.cart import CartSession
from shop.models import ProductModel

def validate_quantity_in_cart_summer(request):
    cart = CartSession(request.session)
    cart_items = cart.get_cart_items()  
    count_product_not_exists = 0
    count_more_quantity_than_stock = 0 
    items_to_remove = []

    for item_key in cart_items.copy(): 
        item = cart_items[item_key]
        stock = item['product_obj'].stock
        quantity = item['quantity']

        if stock == 0:
            items_to_remove.append(item_key)
            count_product_not_exists += 1
        elif quantity > stock:
            cart.update_product_quantity(item_key, stock)
            count_more_quantity_than_stock += 1

    for item_key in items_to_remove:
        cart.remove_product(item_key)

    cart.merge_session_cart_in_db(request.user)

    if count_product_not_exists:
        return {'status': 'warning', 'message': 'محصولاتی که موجودی آنها به اتمام رسیده است حذف شدند.'}
    elif count_more_quantity_than_stock:
        return {'status': 'warning', 'message': 'از آنجایی که تعداد موجودی برخی از محصولات کمتر از تعداد موجودی شما است. تعداد آنها به حداکثر موجودی تغییر یافت'}
    else:
        return {'status': 'ok', 'message': 'سبد خرید با موفقیت آماده شد.'}