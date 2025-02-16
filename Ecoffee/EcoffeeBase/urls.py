from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get-params/', views.get_params, name='get_params'),
    path('redirect/', views.redirect_view, name='redirect'),
]
