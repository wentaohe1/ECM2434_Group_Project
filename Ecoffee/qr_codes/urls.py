from django.urls import path
from . import views

urlpatterns = [
    path('', views.receive_code, name='receive_code'),
    path('qr_summon', views.summon_view, name='qr-summon'),          
    path('get-params/', views.get_params, name='get-params'), 
    path('code/', views.code_redirect_view, name='code-redirect'), 
]