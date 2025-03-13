# shop_dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop_owner_dashboard, name='shop-dashboard'),  
    path('upload-logo/', views.upload_shop_logo, name='shop-upload-logo'),       
]