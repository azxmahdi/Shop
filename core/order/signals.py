from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
from django.core.exceptions import ValidationError

from .models import OrderItemModel
from shop.models import ProductModel


@receiver(post_save, sender=OrderItemModel)
def update_product_quantity(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            product = ProductModel.objects.select_for_update().get(pk=instance.product.pk)
            if product.stock >= instance.quantity:
                product.stock = F('stock') - instance.quantity
                product.save()
            else:
                raise ValidationError(f"موجودی {product.title} کافی نیست!")
