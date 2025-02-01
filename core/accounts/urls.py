from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('reset-password/<str:token>/', views.RestPassword.as_view(), name='reset_password'),
    path('send-mail/reset-password/', views.SendMailRestPassword.as_view(), name='send_mail_reset_password'),
    
]
