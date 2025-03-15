from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login_user', views.login_user,name='login'), 
    path('logout_user', views.logout_user,name='logout'), 
    path('register_user', views.register_user,name='register'), 
    path('password_reset', auth_views.PasswordResetView.as_view(template_name='authenticate/password_reset.html'), name='password_reset'), #Must change to this to allow for custom html
    path('password_reset_done', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/uidb64/token',auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
