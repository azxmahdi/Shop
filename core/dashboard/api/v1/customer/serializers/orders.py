from django.urls import reverse
from rest_framework import serializers

from order.models import OrderItemModel, OrderModel, OrderStatusType
from shop.models import ProductModel


class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.CharField(
        source="category.title", label="عنوان دسته‌بندی"
    )
    price = serializers.DecimalField(
        max_digits=10, decimal_places=0, source="get_price"
    )

    class Meta:
        model = ProductModel
        fields = ["id", "title", "price", "image", "category"]
        ref_name = "CustomerProductDetail"


class OrderItemDetailSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer()
    total_item_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItemModel
        fields = [
            "id",
            "product",
            "quantity",
            "price",
            "total_item_price",
            "created_date",
        ]
        ref_name = "CustomerOrderItemDetail"

    def get_total_item_price(self, obj):
        return obj.quantity * obj.price


class BaseOrderSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    detail_url = serializers.SerializerMethodField()
    invoice_url = serializers.SerializerMethodField()
    user = serializers.EmailField(source="user.email")
    coupon = serializers.CharField(source="coupon.code", allow_null=True)

    class Meta:
        model = OrderModel
        fields = [
            "id",
            "user",
            "address",
            "state",
            "city",
            "zip_code",
            "payment",
            "total_price",
            "coupon",
            "status",
            "created_date",
            "updated_date",
            "detail_url",
            "invoice_url",
            "status_display",
            "full_address",
            "final_price",
        ]
        extra_kwargs = {"status": {"write_only": True}}
        ref_name = "CustomerBaseOrder"

    def get_detail_url(self, obj):
        request = self.context.get("request")
        if not request:
            return None
        return request.build_absolute_uri(
            reverse(
                "dashboard:api-v1:customer:order-detail", kwargs={"pk": obj.pk}
            )
        )

    def get_invoice_url(self, obj):
        request = self.context.get("request")
        if not request or obj.status != OrderStatusType.success.value:
            return None
        return request.build_absolute_uri(
            reverse(
                "dashboard:api-v1:customer:order-invoice",
                kwargs={"pk": obj.pk},
            )
        )

    def get_status_display(self, obj):
        return {
            "id": obj.status,
            "title": obj.get_status()["title"],
            "label": obj.get_status()["label"],
        }

    def get_full_address(self, obj):
        return f"{obj.state}, {obj.city}, {obj.address}"

    def get_final_price(self, obj):
        return obj.get_price()


class OrderListSerializer(BaseOrderSerializer):
    pass


class OrderDetailSerializer(BaseOrderSerializer):
    order_items = OrderItemDetailSerializer(
        many=True, source="order_items.all"
    )

    class Meta(BaseOrderSerializer.Meta):
        fields = BaseOrderSerializer.Meta.fields + ["order_items"]
        ref_name = "CustomerOrderDetail"
