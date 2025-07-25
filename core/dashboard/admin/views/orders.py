from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import FieldError
from django.db.models import Q
from django.views.generic import DetailView, ListView

from dashboard.permissions import HasAdminAccessPermission
from order.models import OrderModel, OrderStatusType


class AdminOrderListView(
    LoginRequiredMixin, HasAdminAccessPermission, ListView
):
    template_name = "dashboard/admin/orders/order-list.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        queryset = OrderModel.objects.all()
        search_q = self.request.GET.get("q")
        if search_q:
            queryset = queryset.filter(
                Q(user__user_profile__first_name__icontains=search_q)
                | Q(user__user_profile__last_name__icontains=search_q)
            )
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        order_by = self.request.GET.get("order_by")
        if order_by:
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.object_list.count()
        context["status_types"] = OrderStatusType.choices
        return context


class AdminOrderDetailView(
    LoginRequiredMixin, HasAdminAccessPermission, DetailView
):
    template_name = "dashboard/admin/orders/order-detail.html"

    def get_queryset(self):
        return OrderModel.objects.all()


class AdminOrderInvoiceView(
    LoginRequiredMixin, HasAdminAccessPermission, DetailView
):
    template_name = "dashboard/admin/orders/order-invoice.html"

    def get_queryset(self):
        return OrderModel.objects.filter(status=OrderStatusType.success.value)
