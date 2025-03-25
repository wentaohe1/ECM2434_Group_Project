from django.contrib import admin
from .models import *


# displays below on the admin page.
admin.site.register(Shop)
admin.site.register(CustomUser)
admin.site.register(Badge)
admin.site.register(ShopUser)
admin.site.register(UserShop)
admin.site.register(UserBadge)
