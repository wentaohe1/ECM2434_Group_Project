# from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, Http404
from django.views.decorators.http import require_POST
from EcoffeeBase.models import Shop, CustomUser, UserShop, Badge, UserBadge
from django.contrib.auth.models import User
from django.utils.timezone import now

def index(request):
    return HttpResponse("Hello, world. You're at the Ecoffee index.")

@require_POST
def log_visit(request):
    '''Updates DB fields for when a user visits a coffee shop'''

    username = request.POST.get("username")
    shop_id = request.POST.get("shop_id")
        
    try:
        user = User.objects.get(username = username)
        custom_user = CustomUser.objects.get(user = user)
        shop = Shop.objects.get(shopId = shop_id)
    except User.DoesNotExist:
        raise Http404("404: User does not exist")
    except CustomUser.DoesNotExist:
        raise Http404("404: User does not exist")
    except Shop.DoesNotExist:
        raise Http404("404: Shop does not exist")
    
    # Updates object fields based on visit
    shop.numberOfVisits += 1
    shop.save()

    custom_user.mostRecentShopId = shop
    custom_user.cupsSaved += 1
    custom_user.lastActiveDateTime = now()

    # Updates user_shop, creating an instance if none
    user_shop, create_new = UserShop.objects.get_or_create(user = custom_user, shopId = shop, defaults = {'visitAmounts': 0})
    user_shop.visitAmounts += 1
    user_shop.save()

    for badge in Badge.objects.all():
        if custom_user.cupsSaved >= badge.coffeeUntilEarned:
            user_badge, create_new = UserBadge.objects.get_or_create(user = custom_user, badgeId = badge)

            custom_user.defaultBadgeId = badge

            user_badge.owned = True # Badge is only created when obtained
            user_badge.dateTimeObtained = now()
            user_badge.save()
    custom_user.save()

    return HttpResponse("Your visit was successfully logged")

    