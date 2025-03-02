from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q, Count

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
        queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value, stock__gt=0)

        if search_q:=self.request.GET.get('q'):
            queryset = queryset.filter(title__icontains=search_q)
        if category_id:=self.request.GET.get('category_id'):
            queryset = queryset.filter(category__id=category_id)
        
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