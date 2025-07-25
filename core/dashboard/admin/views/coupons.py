from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from dashboard.permissions import HasAdminAccessPermission
from order.models import CouponModel

from ..forms.coupons import CouponForm


class AdminCouponListView(
    LoginRequiredMixin, HasAdminAccessPermission, ListView
):
    template_name = "dashboard/admin/coupons/coupon-list.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        queryset = CouponModel.objects.all()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(code__icontains=search_q)
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        return context


class AdminCouponCreateView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    CreateView,
):
    template_name = "dashboard/admin/coupons/coupon-create.html"
    queryset = CouponModel.objects.all()
    form_class = CouponForm
    success_message = "ایجاد کد تخفیف با موفقیت انجام شد"

    def form_valid(self, form):
        coupon = form.save(commit=False)
        coupon.user = self.request.user
        coupon.save()

        messages.success(self.request, self.success_message)
        return redirect(
            reverse_lazy(
                "dashboard:admin:coupon-edit", kwargs={"pk": coupon.pk}
            )
        )

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:coupon-list")


class AdminCouponEditView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    UpdateView,
):
    template_name = "dashboard/admin/coupons/coupon-edit.html"
    queryset = CouponModel.objects.all()
    form_class = CouponForm
    success_message = "ویرایش کد تخفیف با موفقیت انجام شد"

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:admin:coupon-edit", kwargs={"pk": self.get_object().pk}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AdminCouponDeleteView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    DeleteView,
):
    template_name = "dashboard/admin/coupons/coupon-delete.html"
    queryset = CouponModel.objects.all()
    success_url = reverse_lazy("dashboard:admin:coupon-list")
    success_message = "حذف کد تخفیف با موفقیت انجام شد"
