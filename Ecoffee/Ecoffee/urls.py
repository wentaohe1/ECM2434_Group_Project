"""
URL configuration for Ecoffee project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from . import views, settings
from Ecoffee.views import dashboard_view
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.welcome, name="welcome"),
    path('home/', views.home, name='home'),
    path('login_system/', include('django.contrib.auth.urls')),
    path('login_system/', include('login_system.urls')),
    path('EcoffeeBase/', include('EcoffeeBase.urls')),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('code/', include('qr_codes.urls')),
    path('welcome/', views.welcome, name='welcome'),
    path('shop-dashboard/', include('shop_dashboard.urls')),
    path('add_data/', include('add_to_database.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
