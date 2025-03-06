from django.views.generic import TemplateView, FormView, CreateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect

from .forms import ContactForm, NewsLetterForm
from .models import TeamMembers, NewsLetter


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
        messages.success(self.request, "همکاران ما به زودی با شما تماس خواهند گرفت")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "فرم معتبر نیست")
        return super().form_invalid(form)
    

class NewsletterView(CreateView):
    http_method_names = ['post']
    form_class = NewsLetterForm
    success_url = '/'

    def form_valid(self, form):
        messages.success(
            self.request, 'از ثبت نام شما ممنونم، اخبار جدید رو براتون ارسال می کنم 😊👍')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, 'مشکلی در ارسال فرم شما وجود داشت که می دونم برا چی بود!! چون ربات هستید!')
        return redirect('website:index')