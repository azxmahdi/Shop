from typing import Any
from django.views.generic import View, TemplateView
from django.http import JsonResponse

from shop.models import ProductModel, ProductStatusType
from .cart import CartSession
from .validation import is_validate_quantity_product

class SessionAddProductView(View):

    def post(self, request, *args, **kwargs):
        cart = CartSession(request.session)
        product_id = request.POST.get("product_id")
        if is_validate_quantity_product(cart=cart, product_id=product_id):
            cart.add_product(product_id)

        if request.user.is_authenticated:
            cart.merge_session_cart_in_db(request.user)
        return JsonResponse({"cart": cart.get_cart_dict(), "total_quantity": cart.get_total_quantity()})


class SessionRemoveProductView(View):

    def post(self, request, *args, **kwargs):
        cart = CartSession(request.session)
        product_id = request.POST.get("product_id")
        if product_id:
            cart.remove_product(product_id)
        if request.user.is_authenticated:
            cart.merge_session_cart_in_db(request.user)
        return JsonResponse({"cart": cart.get_cart_dict(), "total_quantity": cart.get_total_quantity()})


class SessionUpdateProductQuantityView(View):

    def post(self, request, *args, **kwargs):
        cart = CartSession(request.session)
        product_id = request.POST.get("product_id")
        quantity = request.POST.get("quantity")
        if product_id and quantity:
            cart.update_product_quantity(product_id, quantity)
        if request.user.is_authenticated:
            cart.merge_session_cart_in_db(request.user)
        return JsonResponse({"cart": cart.get_cart_dict(), "total_quantity": cart.get_total_quantity()})


class CartSummaryView(TemplateView):
    template_name = "cart/cart-summary.html"

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        cart = CartSession(self.request.session)
        cart_items = cart.get_cart_items()
        context["cart_items"] = cart_items
        context["total_quantity"] = cart.get_total_quantity()
        context["total_payment_price"] = cart.get_total_payment_amount()
        return context
    

    


class CheckIsProduct(View):
    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': # Check if the request is AJAX
            cart = CartSession(request.session)
            product_id = request.POST.get('product_id')
            if cart.is_product(product_id):
                return JsonResponse({'status': 'ok', "total_payment_product": cart.get_total_product_payment_by_discount(product_id)})
            else:
                return JsonResponse({'status': 'no'})
                

class SessionUpdateProductQuantityDetailView(View):
    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
            cart = CartSession(request.session)
            product_id = request.POST.get('product_id')
            quantity = request.POST.get('quantity')

            try:
                quantity = int(quantity)
                stock = ProductModel.objects.get(id=product_id, status=ProductStatusType.publish.value).stock
                if quantity > stock:
                    cart.update_product_quantity(product_id, 1)
                    return JsonResponse({'status': 'error', 'message': f' متاسفیم. از این کالا فقط {stock} موجود است ', "selected_quantity": cart.get_product_quantity(product_id), "total_quantity": cart.get_total_quantity(), "total_payment_product": cart.get_total_product_payment_by_discount(product_id)})
                
                if quantity <= 0:
                    cart.update_product_quantity(product_id, 1)
                    return JsonResponse({'status': 'error', 'message': f'شما نمی تواند مقدار صفر با منفی وارد کنید', "selected_quantity": cart.get_product_quantity(product_id), "total_quantity": cart.get_total_quantity(), "total_payment_product": cart.get_total_product_payment_by_discount(product_id)})
                
                cart.update_product_quantity(product_id, quantity)
                return JsonResponse({'status': 'success', 'message': f'با موفقیت {quantity} از این کالا در سبد خرید شما ثبت شد', "selected_quantity": cart.get_product_quantity(product_id), "total_quantity": cart.get_total_quantity(), "total_payment_product": cart.get_total_product_payment_by_discount(product_id)})
            except:
                cart.update_product_quantity(product_id, 1)
                return JsonResponse({'status': 'error', 'message': 'لطفا یک مقدار درست وارد کنید', "selected_quantity": cart.get_product_quantity(product_id),"total_quantity": cart.get_total_quantity(), "total_payment_product": cart.get_total_product_payment_by_discount(product_id)})   

