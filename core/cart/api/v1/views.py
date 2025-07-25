import time

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.cart import CartSession
from cart.utils.mixins import CartAPIMixin
from cart.validation import is_validate_quantity_product
from shop.models import ProductModel, ProductStatusType

from .serializers import (
    AddOrRemoveOrCheckIsProductSerializer,
    ProductSerializer,
    UpdateProductQuantitySerializer,
)


class AddProductView(CartAPIMixin, generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AddOrRemoveOrCheckIsProductSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        cart = CartSession(request.session)

        if not serializer.is_valid():
            return self.handle_cart_error(
                "داده‌های وارد شده معتبر نیست",
                status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors,
            )

        product_id = serializer.validated_data["product_id"]
        try:
            if not is_validate_quantity_product(
                cart=cart, product_id=product_id
            ):
                return self.handle_cart_error(
                    "تعداد محصول بیشتر از موجودی انبار است",
                    status.HTTP_400_BAD_REQUEST,
                    product_id=product_id,
                )
        except ProductModel.DoesNotExist:
            return self.handle_cart_error(
                "محصول مورد نظر یافت نشد.", status.HTTP_404_NOT_FOUND
            )

        cart.add_product(product_id)

        return self.finalize_cart(request, cart, product_id)


class RemoveProductView(CartAPIMixin, generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AddOrRemoveOrCheckIsProductSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        cart = CartSession(request.session)

        if not serializer.is_valid():
            return self.handle_cart_error(
                "داده‌های وارد شده معتبر نیست",
                status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors,
            )

        product_id = serializer.validated_data["product_id"]
        if not cart.is_product(product_id):
            return self.handle_cart_error(
                "محصول در سبد خرید وجود ندارد",
                status.HTTP_404_NOT_FOUND,
                product_id=product_id,
            )

        cart.remove_product(product_id)

        return self.finalize_cart(request, cart, product_id)


class UpdateProductQuantityView(CartAPIMixin, generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UpdateProductQuantitySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        cart = CartSession(request.session)

        if not serializer.is_valid():
            return self.handle_cart_error(
                "داده‌های وارد شده معتبر نیست",
                status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors,
            )

        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]

        try:
            quantity = quantity
            product = ProductModel.objects.get(
                id=product_id, status=ProductStatusType.publish.value
            )

            if quantity > product.stock:
                return self.handle_cart_error(
                    f"موجودی کافی نیست (موجودی: {product.stock})",
                    status.HTTP_400_BAD_REQUEST,
                    max_stock=product.stock,
                    product_id=product_id,
                )

            if quantity <= 0:
                return self.handle_cart_error(
                    "مقدار باید بزرگتر از صفر باشد",
                    status.HTTP_400_BAD_REQUEST,
                    product_id=product_id,
                )

            if not cart.is_product(product_id):
                return self.handle_cart_error(
                    "محصول در سبد خرید وجود ندارد",
                    status.HTTP_404_NOT_FOUND,
                    product_id=product_id,
                )

            cart.update_product_quantity(product_id, quantity)

            return self.finalize_cart(request, cart, product_id)

        except ProductModel.DoesNotExist:
            return self.handle_cart_error(
                "محصول یافت نشد",
                status.HTTP_404_NOT_FOUND,
                product_id=product_id,
            )


class CartSummaryView(APIView):

    permission_classes = [
        permissions.AllowAny,
    ]

    def get(self, request, *args, **kwargs):

        cart = CartSession(request.session)

        raw_cart_items_data = cart.get_cart_items()

        serialized_cart_items = {
            product_id: {
                "product_id": product_id,
                "quantity": item_data["quantity"],
                "product": ProductSerializer(item_data["product_obj"]).data,
                "total_price": item_data["total_price"],
            }
            for product_id, item_data in raw_cart_items_data.items()
        }

        total_quantity = cart.get_total_quantity()
        total_price = cart.get_total_payment_amount()
        response_data = {
            "cart_items": serialized_cart_items,
            "total_quantity": total_quantity,
            "total_price": total_price,
            "timestamp": int(time.time()),
        }

        return Response(response_data, status=status.HTTP_200_OK)


class CheckIsProductView(CartAPIMixin, generics.GenericAPIView):
    permission_classes = [
        permissions.AllowAny,
    ]
    serializer_class = AddOrRemoveOrCheckIsProductSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        cart = CartSession(request.session)

        if not serializer.is_valid():
            return self.handle_cart_error(
                "داده‌های وارد شده معتبر نیست",
                status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors,
            )

        product_id = serializer.validated_data["product_id"]

        if cart.is_product(product_id):
            return Response(
                {
                    "status": "ok",
                    "product_id": product_id,
                    "quantity": cart.get_product_quantity(product_id),
                    "total_price": cart.get_total_product_payment_by_discount(
                        product_id
                    ),
                    "timestamp": int(time.time()),
                }
            )
        else:
            return Response(
                {
                    "status": "not_found",
                    "product_id": product_id,
                    "message": "محصول در سبد خرید وجود ندارد",
                    "timestamp": int(time.time()),
                },
                status=status.HTTP_404_NOT_FOUND,
            )
