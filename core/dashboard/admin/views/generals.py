from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from ...permissions import HasAdminAccessPermission



class HomeView(LoginRequiredMixin, HasAdminAccessPermission, TemplateView):
    template_name = 'dashboard/admin/home.html'
