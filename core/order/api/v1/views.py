from decimal import Decimal

from django.db import transaction
from rest_framework import serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cart.cart import CartSession
from cart.models import CartModel
from order.models import OrderItemModel, OrderModel
from order.validations import validate_quantity_in_cart_summer
from payment.models import PaymentModel
from payment.zarinpal_client import ZarinPalSandbox

from .serializers import OrderCheckOutSerializer, ValidateCouponSerializer


class OrderCheckOutAPI(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCheckOutSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        savepoint = transaction.savepoint()

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = request.user
            address = serializer.validated_data["address_id"]
            coupon = serializer.validated_data.get("coupon")

            cart_validation = validate_quantity_in_cart_summer(request)
            if cart_validation["status"] == "warning":
                return Response(
                    {"detail": cart_validation["message"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cart = CartModel.objects.select_for_update().get(user=user)

            order = self.create_order(address, cart, coupon)

            self.create_order_items(order, cart)

            final_price = self.apply_coupon(
                coupon, order, user, cart.calculate_total_price()
            )
            order.total_price = final_price
            order.save()

            payment_url = self.create_payment_request(order)

            self.clear_cart(cart)

            return Response(
                {
                    "status": "success",
                    "message": "سفارش با موفقیت ایجاد شد",
                    "payment_url": payment_url,
                    "order_id": order.id,
                },
                status=status.HTTP_201_CREATED,
            )

        except CartModel.DoesNotExist:
            transaction.savepoint_rollback(savepoint)
            return Response(
                {"error": "سبد خریدی یافت نشد"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            transaction.savepoint_rollback(savepoint)
            return Response(
                {"error": f"خطا در ایجاد سفارش: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def create_order(self, address, cart, coupon):
        return OrderModel.objects.create(
            user=self.request.user,
            address=address.address,
            state=address.state,
            city=address.city,
            zip_code=address.zip_code,
            coupon=coupon,
            total_price=cart.calculate_total_price(),
        )

    def create_order_items(self, order, cart):
        for item in cart.cart_items.all():
            OrderItemModel.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.get_price(),
            )

    def apply_coupon(self, coupon, order, user, total_price):
        if not coupon:
            return total_price

        discount_amount = round(
            total_price * Decimal(coupon.discount_percent / 100)
        )
        final_price = total_price - discount_amount

        coupon.used_by.add(user)
        coupon.save()
        print(final_price)
        return final_price

    def create_payment_request(self, order):
        zarinpal = ZarinPalSandbox()
        response = zarinpal.payment_request(order.total_price)

        if (
            not response
            or "data" not in response
            or "authority" not in response["data"]
        ):
            raise Exception("خطا در ارتباط با درگاه پرداخت")

        authority = response["data"]["authority"]

        payment_obj = PaymentModel.objects.create(
            authority_id=authority,
            amount=order.total_price,
        )
        order.payment = payment_obj
        order.save()
        return zarinpal.generate_payment_url(authority)

    def clear_cart(self, cart):
        cart.cart_items.all().delete()
        CartSession(self.request.session).clear()


class ValidateCouponAPI(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ValidateCouponSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            cart = CartModel.objects.get(user=request.user)
            base_total = cart.calculate_total_price()
            base_tax = round((base_total * 9) / 100)

            return Response(
                {
                    "error": e.detail,
                    "total_tax": base_tax,
                    "total_price": base_total,
                    "valid": False,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        coupon = serializer.validated_data.get("coupon")
        cart = CartModel.objects.get(user=request.user)

        base_total = cart.calculate_total_price()
        base_tax = round((base_total * 9) / 100)

        if coupon:
            discount_percent = coupon.discount_percent / 100
            discounted_total = round(
                base_total - (base_total * discount_percent)
            )
            discounted_tax = round((discounted_total * 9) / 100)

            return Response(
                {
                    "message": "کد تخفیف با موفقیت اعمال شد",
                    "total_tax": discounted_tax,
                    "total_price": discounted_total,
                    "discount_percent": coupon.discount_percent,
                    "discount_amount": base_total - discounted_total,
                    "valid": True,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "کد تخفیف اعمال نشد",
                "total_tax": base_tax,
                "total_price": base_total,
                "valid": False,
            },
            status=status.HTTP_200_OK,
        )
