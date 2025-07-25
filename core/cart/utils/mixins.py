import time

from django.utils import timezone
from rest_framework.response import Response


class CartAPIMixin:
    """Mixin for cart operations with authentication handling"""

    def finalize_cart(self, request, cart, product_id=None):
        """
        Finalize cart operations and return standardized response
        """
        if request.user.is_authenticated:
            cart.merge_session_cart_in_db(request.user)

        response_data = {
            "cart": cart.get_cart_dict(),
            "total_quantity": cart.get_total_quantity(),
            "total_price": cart.get_total_payment_amount(),
            "timestamp": int(time.time()),
        }

        if product_id:
            response_data.update(
                {
                    "product_id": product_id,
                    "product_quantity": cart.get_product_quantity(product_id),
                    "product_total_price": cart.get_total_product_payment_by_discount(
                        product_id
                    ),
                }
            )

        return Response(response_data)

    def handle_cart_error(self, message, status_code, **kwargs):
        """Standardized error response for cart operations"""
        error_data = {
            "status": "error",
            "message": message,
            "timestamp": timezone.now().isoformat(),
        }
        error_data.update(kwargs)
        return Response(error_data, status=status_code)
