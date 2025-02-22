from django.urls import path
from . import views

urlpatterns = [
    path('', views.summon_view, name='qr-summon'),          
    path('get-params/', views.get_params, name='get-params'), 
    path('code/', views.code_redirect_view, name='code-redirect'), 
]