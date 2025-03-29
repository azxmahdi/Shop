from django.db import models
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from datetime import timedelta
from ckeditor_uploader.fields import RichTextUploadingField

class ProductStatusType(models.IntegerChoices):
    publish = 1, ("نمایش")
    draft = 2, ("عدم نمایش")
    not_completed = 3 , ("به صورت کامل ایجاد نشده")


class ProductCategoryModel(models.Model):
    parent = models.ForeignKey(
        'self',  
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name="دسته والد"
    )
    title = models.CharField(max_length=255, verbose_name="عنوان")
    slug = models.SlugField(allow_unicode=True, unique=True, verbose_name="اسلاگ")
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]
        verbose_name = "دسته‌بندی محصول"
        verbose_name_plural = "دسته‌بندی محصولات"
        
    def __str__(self):
        return self.title

    def get_ancestors(self):
        """دریافت تمام دسته‌های والد از ریشه تا این دسته"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors

    def get_all_features_is_required(self):
        """دریافت تمام ویژگی‌های این دسته و دسته‌های والد"""
        from .models import CategoryFeature  # جلوگیری از Import Circular
        features = CategoryFeature.objects.filter(category=self, is_required=True)
        for ancestor in self.get_ancestors():
            features |= CategoryFeature.objects.filter(category=ancestor, is_required=True)
        return features
    
    def get_all_features(self):
        """دریافت تمام ویژگی‌های این دسته و دسته‌های والد"""
        from .models import CategoryFeature  # جلوگیری از Import Circular
        features = CategoryFeature.objects.filter(category=self)
        for ancestor in self.get_ancestors():
            features |= CategoryFeature.objects.filter(category=ancestor)
        return features
    
    def get_all_subcategories(self):
        """
        جمع‌آوری تمام زیردسته‌ها به صورت بازگشتی
        """
        subcategories = list(self.subcategories.all())
        for subcategory in self.subcategories.all():
            subcategories.extend(subcategory.get_all_subcategories())
        return subcategories

    def get_cheapest_product_price(self):
        """
        یافتن ارزان‌ترین محصول در بین تمام زیردسته‌ها
        """
        from django.db.models import Min
        
        # جمع‌آوری تمام زیردسته‌ها + خود دسته والد
        all_categories = [self] + self.get_all_subcategories()
        
        # استخراج IDs تمام دسته‌ها
        category_ids = [cat.id for cat in all_categories]
        
        # کوئری برای یافتن حداقل قیمت
        result = ProductModel.objects.filter(
            category_id__in=category_ids
        ).aggregate(
            min_price=Min('price')
        )
        
        return result['min_price']
    

class CategoryFeature(models.Model):
    category = models.ForeignKey(
        ProductCategoryModel,
        on_delete=models.CASCADE,
        related_name='features',
        verbose_name="دسته مرتبط"
    )
    name = models.CharField(max_length=255, verbose_name="نام ویژگی")
    is_required = models.BooleanField(default=True, verbose_name="اجباری؟")
    
    class Meta:
        verbose_name = "ویژگی دسته"
        verbose_name_plural = "ویژگی‌های دسته‌ها"
    
    def __str__(self):
        return f"{self.category.title} - {self.name}"
    
class FeatureOption(models.Model):
    feature = models.ForeignKey(
        CategoryFeature,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name="ویژگی مرتبط"
    )
    value = models.CharField(max_length=255, verbose_name="مقدار")
    
    class Meta:
        verbose_name = "مقدار ویژگی"
        verbose_name_plural = "مقادیر ویژگی‌ها"
    
    def __str__(self):
        return self.value

class ProductModel(models.Model):
    user = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.PROTECT,
        verbose_name="کاربر ایجادکننده",
        related_name='products'
    )
    category = models.ForeignKey(
        ProductCategoryModel,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="دسته‌بندی"
    )
    title = models.CharField(max_length=255, verbose_name="عنوان")
    slug = models.SlugField(allow_unicode=True, unique=True, verbose_name="اسلاگ")
    image = models.ImageField(
        default="/default/product-image.png",
        upload_to="product/img/",
        verbose_name="تصویر اصلی"
    )
    description = RichTextUploadingField(verbose_name="توضیحات")
    brief_description = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات کوتاه"
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی")
    status = models.IntegerField(
        choices=ProductStatusType.choices,
        default=ProductStatusType.draft.value,
        verbose_name="وضعیت"
    )
    price = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=0,
        verbose_name="قیمت"
    )
    discount_percent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="درصد تخفیف"
    )
    avg_rate = models.FloatField(default=0.0, verbose_name="میانگین امتیاز")
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        indexes = [
            models.Index(fields=['status', '-created_date', '-avg_rate']),
            models.Index(fields=['price']),
        ]
        
    def __str__(self):
        return self.title

    def get_price(self):        
        discount_amount = self.price * Decimal(self.discount_percent / 100)
        discounted_amount = self.price - discount_amount
        return round(discounted_amount)
    
    def is_discounted(self):
        return self.discount_percent != 0
    
    def is_published(self):
        return self.status == ProductStatusType.publish.value
    
    def is_not_completed(self):
        return self.status == ProductStatusType.not_completed.value
    
    
    def is_new(self):
        return self.created_date >= timezone.now() - timedelta(weeks=1)
    
class ProductFeature(models.Model):
    product = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        related_name='features',
        verbose_name="محصول مرتبط"
    )
    feature = models.ForeignKey(
        CategoryFeature,
        on_delete=models.CASCADE,
        verbose_name="ویژگی"
    )
    value = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="مقدار (متنی)"
    )
    option = models.ForeignKey(
        FeatureOption,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="مقدار (از پیش‌تعریف شده)"
    )
    
    class Meta:
        verbose_name = "ویژگی محصول"
        verbose_name_plural = "ویژگی‌های محصولات"
    
    def __str__(self):
        return f"{self.product.title} - {self.feature.name}"

    
class ProductImageModel(models.Model):
    product = models.ForeignKey(ProductModel,on_delete=models.CASCADE,related_name="product_images")
    file = models.ImageField(upload_to="product/extra-img/")
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]


       
class WishlistProductModel(models.Model):
    user = models.ForeignKey("accounts.CustomUser",on_delete=models.PROTECT)
    product = models.ForeignKey(ProductModel,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.product.title

