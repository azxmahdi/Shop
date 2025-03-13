from django.views.generic import ListView, DetailView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q, Count, Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .models import ProductModel, ProductStatusType, ProductCategoryModel, ProductImageModel, WishlistProductModel
from cart.cart import CartSession
from review.models import ReviewModel, ReviewStatusType


class ShopProductGridView(ListView):
    template_name = 'shop/products-grid.html'
    paginate_by = 9


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_items'] = self.get_queryset().count()
        context['categories'] = ProductCategoryModel.objects.all()
        return context
    
    def get_queryset(self):
        queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value).order_by('-stock')

        if search_q:=self.request.GET.get('q'):
            queryset = queryset.filter(title__icontains=search_q)
        if category_id := self.request.GET.get('category_id'):
            category = ProductCategoryModel.objects.filter(id=category_id).first()
            if category:
                if category.parent is None:
                    queryset = queryset.filter(category__in=category.subcategories.all())
                else:
                    queryset = queryset.filter(category=category)

        
        if min_price := self.request.GET.get('min_price'):
            queryset = queryset.filter(price__gte=min_price)
        if max_price := self.request.GET.get('max_price'):
            queryset = queryset.filter(price__lte=max_price)
        
        if order_by:=self.request.GET.get('order_by'):
            queryset = queryset.order_by(order_by)

        page_size = self.request.GET.get('page_size')
        if page_size:
            self.paginate_by = int(page_size)
            
        return queryset



class ShopProductDetailView(DetailView):
    template_name = 'shop/product-overview.html'
    model = ProductModel
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        reviews = ReviewModel.objects.filter(
            product=product,
            status=ReviewStatusType.accepted.value
        )
        
        total_reviews = reviews.count()
        star_counts = reviews.aggregate(
            **{f'star{star}': Count('pk', filter=Q(rate=star)) for star in range(1, 6)}
        )
        
        context['star_counts'] = [
            (
                star,
                star_counts[f'star{star}'],
                round((star_counts[f'star{star}'] / total_reviews * 100)) 
                if total_reviews else 0
            ) 
            for star in reversed(range(1, 6))  # از 5 تا 1
        ]
        
        # درصد توصیهگری (4 یا 5 ستاره)
        recommend_count = reviews.filter(rate__gte=4).count()
        context['recommend_percentage'] = round((recommend_count / total_reviews) * 100) if total_reviews else 0
        
        return context


class AddOrRemoveWishlistView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        product_id = request.POST.get("product_id")
        message = ""
        if product_id:
            try:
                wishlist_item = WishlistProductModel.objects.get(
                    user=request.user, product__id=product_id)
                wishlist_item.delete()
                message = "محصول از لیست علایق حذف شد"
            except WishlistProductModel.DoesNotExist:
                WishlistProductModel.objects.create(
                    user=request.user, product_id=product_id)
                message = "محصول به لیست علایق اضافه شد"

        return JsonResponse({"message": message})
    


class CategoriesSidebar(TemplateView):
    template_name = 'shop/categories-sidebar.html'

    def get_queryset(self):
        # کش کردن ساختار دستهها
        queryset = cache.get('category_tree_queryset')
        if not queryset:
            queryset = ProductCategoryModel.objects.prefetch_related(
                Prefetch(
                    'subcategories',
                    queryset=ProductCategoryModel.objects.all().prefetch_related(
                        Prefetch('subcategories', queryset=ProductCategoryModel.objects.all())
                    )
                )
            ).filter(parent__isnull=True)
            cache.set('category_tree_queryset', queryset, 60*60*24*7)  # 7 روز کش
        return queryset

    def get_min_prices(self):
        min_prices = cache.get('min_prices_data')
        # if not min_prices:
        from django.db.models import Min
        categories = ProductCategoryModel.objects.filter(
            slug__in=["mobile-phones", "mens-clothing", "womens-clothing", "cosmetics"]
        ).prefetch_related('products')
        min_prices = {}
        for category in categories:
            slug_cleaned = category.slug.replace('-', '_')  # تبدیل - به _
            min_price = category.products.aggregate(min_price=Min('price'))['min_price']
            min_prices[f"min_price_{slug_cleaned}"] = {
                'id': category.id,
                'min_price': min_price
            }
        cache.set('min_prices_data', min_prices, 60*60*24*7)
        return min_prices

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. ساختار دستهبندی (کش شده)
        root_categories = self.get_queryset()
        
        def build_tree(category):
            return {
                'category': category,
                'children': [build_tree(child) for child in category.subcategories.all()]
            }
        context['category_tree'] = [build_tree(cat) for cat in root_categories]
        
        # 2. حداقل قیمتها (کش شده)
        context.update(self.get_min_prices())
        
        # 3. محصولات پرطرفدار (بدون کش)
        context["poplar_products"] = ProductModel.objects.select_related(
            'category', 'user'
        ).filter(
            status=ProductStatusType.publish.value
        ).order_by("-created_date", "-avg_rate")[:3]
        
        return context
