from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from ...permissions import HasAdminAccessPermission


class HomeView(LoginRequiredMixin, HasAdminAccessPermission, TemplateView):
    template_name = "dashboard/admin/home.html"
