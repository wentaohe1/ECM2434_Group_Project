from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('log_visit/', views.log_visit, name = 'log_visit'),
]
