from django.contrib import admin
from .models import ProductModel, ProductImageModel, ProductCategoryModel, CategoryFeature, FeatureOption,ProductFeature ,WishlistProductModel

@admin.register(ProductCategoryModel)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'parent', 'created_date')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}

@admin.register(CategoryFeature)
class CategoryFeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_required')
    list_filter = ('category', 'is_required')

@admin.register(FeatureOption)
class FeatureOptionAdmin(admin.ModelAdmin):
    list_display = ('value', 'feature')
    list_filter = ('feature',)

@admin.register(ProductModel)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'discount_percent', 'status', 'created_date')
    list_filter = ('status', 'category')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ProductFeature)
class ProductFeatureAdmin(admin.ModelAdmin):
    list_display = ('product', 'feature', 'value', 'option')
    list_filter = ('product', 'feature')

@admin.register(ProductImageModel)
class ProductImageModelAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "created_date")

@admin.register(WishlistProductModel)
class WishlistProductModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product")
