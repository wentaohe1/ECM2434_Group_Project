from django.db import models
from EcoffeeBase.models import Shop

class ShopLogo(models.Model):
    shop = models.OneToOneField(
        Shop, 
        on_delete=models.CASCADE,
        related_name='logo'
    )
    logo = models.ImageField(upload_to='shop_logos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shop.shop_name} Logo"