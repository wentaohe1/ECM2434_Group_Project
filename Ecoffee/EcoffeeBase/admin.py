from django.contrib import admin

from EcoffeeBase.models import User, Badge, Shop, UserShop, Coffee, UserBadge

admin.site.register(User)
admin.site.register(Badge)
admin.site.register(Shop)
admin.site.register(UserShop)
admin.site.register(Coffee)
admin.site.register(UserBadge)
