from django.shortcuts import redirect,render
from EcoffeeBase.models import *
from datetime import datetime
import hmac
import time
from django.http import JsonResponse
SECRET_KEY = b'coffee-secret-key-2024'

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
                user.last_active_date_time = datetime.now()
                # need to run a trigger to check if the badge needs to be updated.
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

def generate_params():
    timestamp = int(time.time() // 120) * 120
    signature = hmac.new(SECRET_KEY, str(timestamp).encode(), 'sha256').hexdigest()
    return {'t': timestamp, 'sig': signature}

def summon_view(request):
    return render(request, 'summon.html')

def get_params(request):
    return JsonResponse(generate_params())

def code_redirect_view(request):
    timestamp = request.GET.get('t', '')
    sig = request.GET.get('sig', '')
    
    expected_sig = hmac.new(SECRET_KEY, str(timestamp).encode(), 'sha256').hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        return JsonResponse({'status': 'invalid signature'}, status=403)
    
    if int(time.time()) - int(timestamp) > 120:
        return JsonResponse({'status': 'expired'}, status=410)
    
    return redirect('http://127.0.0.1:8000/code/?code=0001')

"""Orders the badges, increments through them until it finds one that is larger than the number of cups you have saved."""


def check_badge_progress(relevant_user):
    for badge in Badge.objects.order_by("coffee_until_earned"):
        if relevant_user.cups_saved >= badge.coffee_until_earned:
            relevant_user.default_badge_id = badge
            # this updates the user badges(actual implementaion in the dashbaord will be added next sprint)
            # search_result = UserBadge.objects.filter(user=relevant_user.user, badge_id=badge)
            # if not search_result.exists():  # check if the user-badge relation already exists
            #    current_date_time = datetime.now()
            #    x = UserBadge(user=relevant_user.user, badge_id=badge,
            #                  date_time_obtained=current_date_time)
            #    x.save()
