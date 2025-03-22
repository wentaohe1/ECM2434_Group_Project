from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import verify_email

urlpatterns = [
    path('login_user', views.login_user,name='login'), 
    path('logout_user', views.logout_user,name='logout'), 
    path('register_user', views.register_user,name='register'), 
    path('password_reset', views.password_reset, name='password_reset'),
    path('password_reset_done', views.password_reset_done, name='password_reset_done'),
    path('password_reset_complete/<uidb64>/<token>/', views.password_reset_complete, name="password_reset_complete"),
    path('password_reset_confirm', views.password_reset_confirm, name='password_reset_confirm'),
    path('verify_email/<str:token>/', verify_email, name='verify_email'),
]
