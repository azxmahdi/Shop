from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .models import OrderModel, OrderItemModel, OrderStatusType
from shop.models import ProductModel
@shared_task
def cancel_expired_pending_orders():
    cutoff_time = timezone.now() - timedelta(minutes=11)
    
    with transaction.atomic():
        pending_orders = OrderModel.objects.select_for_update().filter(
            status=OrderStatusType.pending.value,
            created_date__lte=cutoff_time
        )
        
        
        for order in pending_orders:
            order.status = OrderStatusType.failed.value
            order.save()
            
            for order_item in order.order_items.all():
                product = order_item.product
                product.stock += order_item.quantity
                product.save()
                
                order_item.delete()
