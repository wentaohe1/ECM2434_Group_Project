# from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, Http404
from django.views.decorators.http import require_POST
from EcoffeeBase.models import Shop, User, UserShop, Badge, UserBadge, Coffee
from django.utils.timezone import now

def index(request):
    return HttpResponse("Hello, world. You're at the Ecoffee index.")

@require_POST
def log_visit(request):
    '''Updates DB fields for when a user visits a coffee shop'''

    userId = request.POST.get("userId")
    shopId = request.POST.get("shopId")
    coffeeName = request.POST.get("coffeeName")
        
    try:
        user = User.objects.get(userId = userId)
        shop = Shop.objects.get(shopId = shopId)
        coffee = Coffee.objects.get(name = coffeeName)
    except User.DoesNotExist:
        raise Http404("404: User does not exist")
    except Shop.DoesNotExist:
        raise Http404("404: Shop does not exist")
    except Coffee.DoesNotExist:
        Coffee.objects.create(name = coffeeName, numberOrdered = 0)
        coffee = Coffee.objects.get(name = coffeeName)
    
    # Updates object fields based on visit
    shop.numberOfVisits += 1
    shop.save()

    coffee.numberOrdered += 1
    coffee.lastOrdered = now()
    coffee.save()

    user.mostRecentShopId = shop
    user.progression += 1
    user.cupsSaved += 1
    user.lastActiveDateTime = now()

    # Updates userShop, creating an instance if none
    userShop, create_new = UserShop.objects.get_or_create(userId = user, shopId = shop, defaults = {'visitAmounts': 0})
    userShop.visitAmounts += 1
    userShop.save()

    for badge in Badge.objects.all():
        if user.cupsSaved >= badge.coffeeUntilEarned:
            userBadge, create_new = UserBadge.objects.get_or_create(userId = user, badgeId = badge)

            user.progression = 0
            user.defaultBadgeId = badge

            userBadge.owned = True # Badge is only created when obtained
            userBadge.dateTimeObtained = now()
            userBadge.save()
    user.save()

    return HttpResponse("Your visit was successfully logged")

    