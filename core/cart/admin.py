from django.contrib import admin

from .models import CartItemModel, CartModel


@admin.register(CartModel)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user")


@admin.register(CartItemModel)
class CartItemModelAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity")
