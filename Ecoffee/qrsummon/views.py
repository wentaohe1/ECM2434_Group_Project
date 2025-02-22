import hmac
import time
from django.http import JsonResponse
from django.shortcuts import render, redirect

SECRET_KEY = b'coffee-secret-key-2024'

def generate_params():
    timestamp = int(time.time() // 120) * 120
    signature = hmac.new(SECRET_KEY, str(timestamp).encode(), 'sha256').hexdigest()
    return {'t': timestamp, 'sig': signature}

def summon_view(request):
    return render(request, 'qrsummon/summon.html')

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