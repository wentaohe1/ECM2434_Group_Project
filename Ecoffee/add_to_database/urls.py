from django.urls import path
from . import views

urlpatterns = [
    path('add_shop', views.add_shop, name='add_shop'),
    path('add_coffee', views.add_coffee, name='add_coffee'),
    path('add_badge', views.add_badge, name='add_badge'),
    path('shop_owner/<int:shop_id>', views.shop_owner, name='shop_owner'),
    path('upload_logo/<int:shop_id>', views.upload_logo, name='upload-logo'),
    path('', views.receive_code, name='receive_code'),
]
