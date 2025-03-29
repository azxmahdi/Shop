from typing import Any
from django.db.models.base import Model as Model

from django.views.generic import (
    View,
    TemplateView,
    UpdateView,
    ListView,
    DeleteView,
    CreateView,
    FormView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasAdminAccessPermission
from django.contrib.auth import views as auth_views
from dashboard.admin.forms import *
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from accounts.models import Profile
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404
from shop.models import ProductModel, ProductCategoryModel, ProductStatusType, ProductFeature
from django.core.exceptions import FieldError


from ..forms import ProductImageForm, ProductFeatureForm
from shop.models import ProductModel, ProductImageModel, ProductStatusType, ProductCategoryModel, CategoryFeature, FeatureOption

class AdminProductListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/products/product-list.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        queryset = ProductModel.objects.all()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(title__icontains=search_q)
        if category_id := self.request.GET.get("category_id"):
            queryset = queryset.filter(category__id=category_id)
        if min_price := self.request.GET.get("min_price"):
            queryset = queryset.filter(price__gte=min_price)
        if max_price := self.request.GET.get("max_price"):
            queryset = queryset.filter(price__lte=max_price)
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        context["categories"] = ProductCategoryModel.objects.all()
        return context


class AdminProductCreateView(LoginRequiredMixin, HasAdminAccessPermission, CreateView):
    template_name = "dashboard/admin/products/product-create.html"
    queryset = ProductModel.objects.all()
    form_class = ProductForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        status = form.cleaned_data["status"]
        form.instance.status = ProductStatusType.not_completed.value
        super().form_valid(form)
        return redirect(reverse_lazy("dashboard:admin:add-product-feature", kwargs={"product_id": form.instance.pk, "status":status}))

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:product-list")


class AdminProductEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/products/product-edit.html"
    queryset = ProductModel.objects.all()
    form_class = ProductForm
    success_message = "ویرایش محصول با موفقیت انجام شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:product-edit", kwargs={"pk": self.get_object().pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["image_form"] = ProductImageForm()
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.product_images.prefetch_related()
        return obj


class AdminProductDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/products/product-delete.html"
    queryset = ProductModel.objects.all()
    success_url = reverse_lazy("dashboard:admin:product-list")
    success_message = "حذف محصول با موفقیت انجام شد"


class AdminProductAddImageView(LoginRequiredMixin, HasAdminAccessPermission, CreateView):
    http_method_names = ['post']
    form_class = ProductImageForm

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:product-edit', kwargs={'pk': self.kwargs.get('pk')})

    def get_queryset(self):
        return ProductImageModel.objects.filter(product__id=self.kwargs.get('pk'))

    def form_valid(self, form):
        form.instance.product = ProductModel.objects.get(
            pk=self.kwargs.get('pk'))
        # handle successful form submission
        messages.success(
            self.request, 'تصویر مورد نظر با موفقیت ثبت شد')
        return super().form_valid(form)

    def form_invalid(self, form):
        # handle unsuccessful form submission
        messages.error(
            self.request, 'اشکالی در ارسال تصویر رخ داد لطفا مجدد امتحان نمایید')
        return redirect(reverse_lazy('dashboard:admin:product-edit', kwargs={'pk': self.kwargs.get('pk')}))


class AdminProductRemoveImageView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    http_method_names = ["post"]
    success_message = "تصویر مورد نظر با موفقیت حذف شد"

    def get_queryset(self):
        return ProductImageModel.objects.filter(product__id=self.kwargs.get('pk'))
    
    def get_object(self, queryset=None):
        return self.get_queryset().get(pk=self.kwargs.get('image_id'))

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:product-edit', kwargs={'pk': self.kwargs.get('pk')})

    def form_invalid(self, form):
        messages.error(
            self.request, 'اشکالی در حذف تصویر رخ داد لطفا مجدد امتحان نمایید')
        return redirect(reverse_lazy('dashboard:admin:product-edit', kwargs={'pk': self.kwargs.get('pk')}))
    


class AdminAddProductFeatureFormView(LoginRequiredMixin, HasAdminAccessPermission, FormView):
    template_name = 'dashboard/admin/products/add-product-feature.html'
    form_class = ProductFeatureForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.product = get_object_or_404(
            ProductModel,
            id=self.kwargs['product_id']
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['product_id'] = self.product.id
        return kwargs

    def form_valid(self, form):
        ProductFeature.objects.filter(product=self.product).delete()
        
        for field_name, value in form.cleaned_data.items():
            feature_id = field_name.split('_')[-1]
            feature = get_object_or_404(CategoryFeature, id=feature_id)
            
            if not value and not feature.is_required:
                continue  
            
            if feature.options.exists():
                option = get_object_or_404(FeatureOption, id=value)
                ProductFeature.objects.create(
                    product=self.product,
                    feature=feature,
                    option=option
                )
            else:
                ProductFeature.objects.create(
                    product=self.product,
                    feature=feature,
                    value=value
                )
        product = ProductModel.objects.get(pk=self.product.pk)
        product.status = self.kwargs["status"]
        product.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:admin:product-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

class AdminEditProductFeatureFormView(FormView):
    template_name = 'dashboard/admin/products/edit-product-feature.html'
    form_class = ProductFeatureForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.product = get_object_or_404(
            ProductModel,
            id=self.kwargs['product_id']
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['product_id'] = self.product.id
        return kwargs

    def form_valid(self, form):
        ProductFeature.objects.filter(product=self.product).delete()
        
        for field_name, value in form.cleaned_data.items():
            feature_id = field_name.split('_')[-1]
            feature = get_object_or_404(CategoryFeature, id=feature_id)
            
            if not value and not feature.is_required:
                continue  
            
            if feature.options.exists():
                option = get_object_or_404(FeatureOption, id=value)
                ProductFeature.objects.create(
                    product=self.product,
                    feature=feature,
                    option=option
                )
            else:
                ProductFeature.objects.create(
                    product=self.product,
                    feature=feature,
                    value=value
                )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:admin:product-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context