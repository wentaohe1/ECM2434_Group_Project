from django.urls import path
from . import views

urlpatterns = [
    path('add_new_data', views.add_new_data, name='add_new_data'),
]