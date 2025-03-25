from django.shortcuts import redirect
from EcoffeeBase.models import *
from datetime import datetime


def receive_code(request):
    code = str(request.GET.get('code', 'No code provided'))
    try:
        # find part of the code which is relavent to the shop
        # for now, first 4 letters, allows for expansion later.
        shop_code = read_shop_code(code, 4)
        shop = Shop.objects.get(active_code=int(shop_code))
        shop.number_of_visits += 1
        if request.user.is_authenticated:
            try:
                # Updates information relevant to the users order.
                request_user = request.user
                user = CustomUser.objects.get(user=request_user)
                user.cups_saved += 1
                check_badge_progress(user)
                user.most_recent_shop_id = shop
                user.last_active_date_time = now()
                time = now()
                create_new_user_shop(shop, user)
                streak_day_difference = time.date() - user.streak_start_day
                if streak_day_difference.days == user.streak:
                    user.streak += 1
                elif streak_day_difference.days >= user.streak:
                    user.streak = time.date()
                user.save()
                shop.save()  # saves after everything is confirmed okay, changes will rollback (by default after a request has returned) if not
                return redirect('home')
            except CustomUser.DoesNotExist:
                return redirect('register')
        else:
            # user not logged in has to login/create account
            return redirect('login')
    except Shop.DoesNotExist:
        return redirect('home')


def read_shop_code(code, number_of_letters):
    return code[:number_of_letters]


"""Orders the badges, increments through them until it finds one that is larger than the number of cups you have saved."""


def check_badge_progress(relevant_user):
    for badge in Badge.objects.order_by("coffee_until_earned"):
        if relevant_user.cups_saved >= badge.coffee_until_earned:
            relevant_user.default_badge_id = badge
            user_badge = UserBadge.objects.filter(
                user=relevant_user, badge_id=badge).first()
            if not user_badge:
                current_date_time = timezone.now()
                user_badge = UserBadge(user=relevant_user, badge_id=badge,
                                       date_time_obtained=current_date_time)
                user_badge.save()


def create_new_user_shop(shop, request_custom_user):
    user_shop = UserShop.objects.filter(
        shop_id=shop, user=request_custom_user).first()
    if user_shop:
        user_shop.visit_amounts += 1
    else:
        user_shop = UserShop.objects.create(
            user=request_custom_user, shop_id=shop, visit_amounts=1)
    user_shop.save()
