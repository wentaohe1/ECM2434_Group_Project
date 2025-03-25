from django.urls import path
from . import views

urlpatterns = [
    path('', views.receive_code, name='receive_code'),
]
