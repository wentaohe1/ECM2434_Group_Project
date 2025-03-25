from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('add_shop', views.add_shop, name='add_shop'),
    path('shop_owner/<int:shop_id>', views.shop_owner, name='shop_owner'),
    path('upload_logo/<int:shop_id>', views.upload_logo, name='upload-logo'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
