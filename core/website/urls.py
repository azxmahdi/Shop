from django.urls import path


from . import views


app_name = 'website'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name='index'),
    path('about/', views.AboutTemplateView.as_view(), name='about'),
    path('contact/', views.ContactTemplateView.as_view(), name='contact'),
]
