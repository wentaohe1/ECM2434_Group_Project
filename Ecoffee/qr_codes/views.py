from django.shortcuts import redirect, render
from EcoffeeBase.models import *
from datetime import datetime
import hmac
import time
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist

SECRET_KEY = b'coffee-secret-key-2024'

def receive_code(request):
    code = request.GET.get('code')
    timestamp = request.GET.get('t')
    sig = request.GET.get('sig')
    
    if not all([code, timestamp, sig]):
        return HttpResponseBadRequest("Missing required parameters: code, t, or sig")

    try:
        if len(code) < 4 or not code[:4].isdigit():
            raise ValueError("Invalid shop code format (first 4 chars must be digits)")
        shop_code = int(code[:4])

        expected_sig = hmac.new(SECRET_KEY, timestamp.encode(), 'sha256').hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return HttpResponseBadRequest("Invalid signature")

        if int(time.time()) - int(timestamp) > 120:
            return HttpResponseBadRequest("QR code expired")

        shop = Shop.objects.get(active_code=shop_code)
        shop.number_of_visits += 1
        
        if request.user.is_authenticated:
            try:
                user = CustomUser.objects.get(user=request.user)
                user.cups_saved += 1
                check_badge_progress(user)
                user.most_recent_shop_id = shop
                user.last_active_date_time = datetime.now()
                user.save()
                shop.save()
                return redirect('home')
            except CustomUser.DoesNotExist:
                return redirect('register')
        else:
            return redirect('login')

    except ValueError as e:
        return HttpResponseBadRequest(str(e))
    except Shop.DoesNotExist:
        return redirect('home')

def code_redirect_view(request):
    timestamp = request.GET.get('t', '')
    sig = request.GET.get('sig', '')
    
    if not timestamp or not sig:
        return JsonResponse({'status': 'missing parameters'}, status=400)
    
    redirect_url = f'http://127.0.0.1:8000/code/?code=0001&t={timestamp}&sig={sig}'
    return redirect(redirect_url)

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

def check_badge_progress(relevant_user):
    for badge in Badge.objects.order_by("coffee_until_earned"):
        if relevant_user.cups_saved >= badge.coffee_until_earned:
            relevant_user.default_badge_id = badge
            relevant_user.save()
