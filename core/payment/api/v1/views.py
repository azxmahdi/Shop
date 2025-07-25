import logging

from django.conf import settings
from django.db import transaction
from django.urls import reverse
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from order.models import OrderModel, OrderStatusType
from payment.models import PaymentModel, PaymentStatusType
from payment.zarinpal_client import ZarinPalSandbox

logger = logging.getLogger(__name__)


class PaymentVerifyAPI(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        authority_id = request.query_params.get("Authority")
        gateway_status = request.query_params.get("Status")

        if not authority_id or not gateway_status:
            logger.warning(
                "پارامترهای ضروری در تأیید پرداخت وجود ندارد",
                extra={
                    "user": request.user.id,
                    "params": request.query_params,
                },
            )
            return Response(
                {"detail": "پارامترهای Authority و Status الزامی هستند"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if gateway_status != "OK":
            logger.info(
                "پرداخت توسط کاربر لغو شد",
                extra={"user": request.user.id, "authority": authority_id},
            )
            return Response(
                {
                    "status": "failed",
                    "detail": "پرداخت توسط کاربر لغو شد یا با خطا مواجه شد",
                    "next_step": reverse("order:failed"),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = PaymentModel.objects.select_for_update().get(
                authority_id=authority_id
            )

            try:
                order = OrderModel.objects.select_for_update().get(
                    payment=payment
                )
            except OrderModel.DoesNotExist:
                logger.error(
                    "هیچ سفارشی برای این پرداخت یافت نشد",
                    extra={
                        "authority": authority_id,
                        "payment_id": payment.id,
                    },
                )
                return Response(
                    {"detail": "سفارش مرتبط با این پرداخت یافت نشد"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except OrderModel.MultipleObjectsReturned:
                logger.critical(
                    "چندین سفارش برای یک پرداخت",
                    extra={
                        "authority": authority_id,
                        "payment_id": payment.id,
                    },
                )
                return Response(
                    {
                        "detail": "خطای سیستمی: چندین سفارش برای این پرداخت وجود دارد"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            if order.user != request.user:
                logger.warning(
                    "کاربر غیرمجاز سعی در تأیید پرداخت داشت",
                    extra={
                        "user": request.user.id,
                        "order_user": order.user.id,
                        "authority": authority_id,
                    },
                )
                return Response(
                    {"detail": "شما مجوز تأیید این پرداخت را ندارید"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if payment.status == PaymentStatusType.success.value:
                logger.info(
                    "درخواست تأیید مجدد برای پرداخت موفق",
                    extra={"user": request.user.id, "authority": authority_id},
                )
                return Response(
                    {
                        "status": "success",
                        "detail": "این پرداخت قبلاً با موفقیت تأیید شده است",
                        "ref_id": payment.ref_id,
                        "next_step": reverse("order:completed"),
                    },
                    status=status.HTTP_200_OK,
                )

            zarinpal = ZarinPalSandbox(merchant_id=settings.MERCHANT_ID)
            response = zarinpal.payment_verify(
                amount=int(payment.amount), authority=authority_id
            )

            status_code = response.get("Status")
            ref_id = response.get("RefID")

            payment.ref_id = ref_id
            payment.response_code = status_code
            payment.response_json = response

            if status_code in [100, 101]:
                payment.status = PaymentStatusType.success.value
                order_status = OrderStatusType.success.value
                detail_message = "پرداخت با موفقیت تأیید شد"
                next_step = reverse("order:completed")
            else:
                payment.status = PaymentStatusType.failed.value
                order_status = OrderStatusType.failed.value
                detail_message = f"پرداخت ناموفق (کد خطا: {status_code})"
                next_step = reverse("order:failed")

            payment.save()

            order.status = order_status
            order.save()

            logger.info(
                f"پرداخت با وضعیت {'موفق' if status_code in [100, 101] else 'ناموفق'} تأیید شد",
                extra={
                    "user": request.user.id,
                    "order_id": order.id,
                    "amount": payment.amount,
                    "ref_id": ref_id,
                    "status_code": status_code,
                },
            )

            return Response(
                {
                    "status": (
                        "success" if status_code in [100, 101] else "failed"
                    ),
                    "detail": detail_message,
                    "ref_id": ref_id,
                    "order_id": order.id,
                    "amount": payment.amount,
                    "next_step": next_step,
                },
                status=status.HTTP_200_OK,
            )

        except PaymentModel.DoesNotExist:
            logger.error(
                "تراکنش یافت نشد",
                extra={"authority": authority_id, "user": request.user.id},
            )
            return Response(
                {"detail": "تراکنش یافت نشد"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception:
            logger.exception(
                "خطای داخلی در تأیید پرداخت",
                extra={"authority": authority_id, "user": request.user.id},
            )
            return Response(
                {"detail": "خطای داخلی سرور در تأیید پرداخت"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
