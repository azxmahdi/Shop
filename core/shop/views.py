from django.views.generic import ListView, DetailView

from .models import ProductModel, ProductStatusType, ProductCategoryModel
from cart.cart import CartSession

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
        cart = CartSession(self.request.session)
        context["selected_quantity"] = cart.get_product_quantity(self.object.id)
        print(self.object.id)
        print(context["selected_quantity"])
        return context