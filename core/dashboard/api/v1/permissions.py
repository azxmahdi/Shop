from rest_framework import permissions

from accounts.models import UserType


class IsAdminOrSuperUser(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return (
            request.user.type == UserType.admin.value
            or request.user.type == UserType.superuser.value
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsCustomer(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.type == UserType.customer.value

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
