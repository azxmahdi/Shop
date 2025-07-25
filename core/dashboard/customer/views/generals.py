from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from dashboard.permissions import HasCustomerAccessPermission


class HomeView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = "dashboard/customer/home.html"
