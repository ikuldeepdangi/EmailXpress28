from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('send-email/', views.send_email_view, name='send_email'),
    path('success/', views.success_view, name='success'),
]
