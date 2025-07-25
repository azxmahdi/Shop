from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import ProductModel


@receiver(post_save, sender=ProductModel)
@receiver(post_delete, sender=ProductModel)
def invalidate_min_prices_cache(sender, instance, **kwargs):
    cache.delete("min_prices_data")
