from django.shortcuts import render,redirect
from django.http import HttpResponse
from EcoffeeBase.models import *
from datetime import datetime


def receive_code(request):
    code = str(request.GET.get('code', 'No code provided'))
    try:
        #find part of the code which is relavent to the shop
        shop_code=read_shop_code(code,4)#for now, first 4 letters, allows for expansion later.
        shop=Shop.objects.get(activeCode=int(shop_code))
        shop.numberOfVisits+=1
        if request.user.is_authenticated:
            try:
                username=request.user #Updates information relevant to the users order.
                user=CustomUser.objects.get(user=username)
                user.cupsSaved+=1
                user.mostRecentShopId=shop
                #trigger for updating progression and best badge
                update_progression(user)
                user.lastActiveDateTime=datetime.now()
                shop.number_of_visits += 1
                user_shop_object = UserShop.objects.get(username=username, shop_id=shop.shop_id)
                user_shop_object.visit_amounts += 1
                user_shop_object.save()
                user.save()
                shop.save() #saves after everything is confirmed okay, changes will rollback (by default after a request has returned) if not
                return redirect('home')
            except CustomUser.DoesNotExist:
                return redirect('register')
        else:
            #user not logged in has to login/create account
            return redirect('login')
    except Shop.DoesNotExist:
        return redirect('home')

def update_progression(user_object):
    cups_saved = user_object.cupsSaved
    badge_objects = Badge.objects.order_by("coffee_until_earned")
    if badge_objects.count() == 0: #no badge made yet
        return
    if badge_objects.first().coffee_until_earned > cups_saved: #user do not have enough cup daved for first badge
        return
    if badge_objects.first().coffee_until_earned <= cups_saved < badge_objects[1].cofee_until_earned: # user can only get first badge
        update_badge(user_object, badge_objects.first())
        return
    new_badge = badge_objects.first()
    for badge_object in badge_objects[1:]: # check if the user can get which badge form the second one onward
        last_badge = new_badge
        new_badge = badge_object
        if last_badge.coffee_until_earned <= cups_saved < new_badge.coffee_until_earned:
            update_badge(user_object, last_badge)
            progression = (cups_saved - last_badge.coffee_until_earned) / (
                new_badge.coffee_until_earned - last_badge.coffee_until_earned)
            user_object.progression = round(progression * 100)
            user_object.save()
            return
    user_object.progression = 100
    user_object.save()
    update_badge(user_object, new_badge)
    return


#add a user-badge relation record if there does not exit one already
def update_badge(user_object, badge):
    badge_id = badge.badge_id
    username = user_object.username
    search_result = UserBadge.objects.filter(username=username, badge_id=badge_id)
    if not search_result.exists(): # check if the user-badge relation already exists
        user_object.default_badge_id = badge_id
        current_date_time = datetime.now()
        x = UserBadge(username=username, badge_id=badge_id,
                      date_time_obtained=current_date_time)
        x.save()
    return


def read_shop_code(code,number_of_letters):
    return code[:number_of_letters]
