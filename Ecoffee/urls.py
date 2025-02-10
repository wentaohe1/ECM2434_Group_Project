from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('EcoffeeBase.urls')),
    path('login/', include('login_system.urls')),
    path('register/', include('login_system.urls')),
] 
