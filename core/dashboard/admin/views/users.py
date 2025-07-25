from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.db.models import ProtectedError
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView, UpdateView

from dashboard.admin.forms import *
from dashboard.permissions import *

User = get_user_model()


class UserListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    title = "لیست کاربران"
    template_name = "dashboard/admin/users/user-list.html"
    paginate_by = 10
    ordering = "-created_date"

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        queryset = User.objects.all()

        if self.request.user.type == UserType.admin.value:
            queryset = queryset.filter(
                type=UserType.customer.value, is_superuser=False
            )

        if search_query := self.request.GET.get("q"):
            queryset = queryset.filter(email__icontains=search_query)

        if ordering := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(ordering)
            except FieldError:
                queryset = queryset.order_by(self.ordering)
        else:
            queryset = queryset.order_by(self.ordering)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        return context


class UserDeleteView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    DeleteView,
):
    title = "حذف کاربر"
    template_name = "dashboard/admin/users/user-delete.html"
    success_url = reverse_lazy("dashboard:admin:user-list")
    success_message = "کاربر مورد نظر با موفقیت حذف شد"

    def get_queryset(self):
        user = self.request.user
        if user.type == UserType.admin.value:
            return User.objects.filter(
                is_superuser=False, type=UserType.customer.value
            )
        elif user.type == UserType.superuser.value:
            return User.objects.all()
        else:
            return User.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = self.get_object()
        return context

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.products.exists():
            messages.error(request, "این کاربر دارای محصولات مرتبط است.")
            return redirect("dashboard:admin:user-edit", pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request, "حذف ناموفق: این کاربر دارای روابط اجباری است."
            )
            return redirect("dashboard:admin:user-list")


class UserUpdateView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    UpdateView,
):
    title = "ویرایش کاربر"
    template_name = "dashboard/admin/users/user-edit.html"
    success_message = "کاربر مورد نظر با موفقیت ویرایش شد"

    def get_form_class(self):
        return UserForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:admin:user-edit", kwargs={"pk": self.kwargs.get("pk")}
        )

    def get_queryset(self):
        base_queryset = User.objects.all()

        if self.request.user.type == UserType.admin.value:
            return base_queryset.filter(
                type__in=[UserType.customer.value, UserType.admin.value],
                is_superuser=False,
            )
        return base_queryset

    def form_valid(self, form):
        user = form.save(commit=False)

        user.email = self.get_object().email

        if self.request.user.type != UserType.superuser.value:
            if "type" in form.changed_data:
                form.add_error("type", "شما مجوز تغییر نوع کاربر را ندارید")
                return self.form_invalid(form)

            user.type = self.get_object().type
            user.is_superuser = self.get_object().is_superuser

        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        target_user = self.get_object()

        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if target_user.is_superuser:
            return HttpResponseForbidden("شما مجوز ویرایش این کاربر را ندارید")

        return super().dispatch(request, *args, **kwargs)
