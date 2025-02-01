from django.views.generic import TemplateView, FormView
from django.contrib import messages
from django.urls import reverse_lazy

from .forms import ContactForm
from .models import TeamMembers


class IndexTemplateView(TemplateView):
    template_name = 'website/index.html'


class AboutTemplateView(TemplateView):
    template_name = 'website/about.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['members'] = TeamMembers.objects.filter(status=True)
        return context




class ContactTemplateView(FormView):
    template_name = 'website/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('website:index')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Our colleagues will contact you soon")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "The form is not valid")
        return super().form_invalid(form)