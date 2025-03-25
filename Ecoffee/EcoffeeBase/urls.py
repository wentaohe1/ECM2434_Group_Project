from django.urls import path
from . import views

urlpatterns = [
    path('log_visit/', views.log_visit, name='log_visit')
]
