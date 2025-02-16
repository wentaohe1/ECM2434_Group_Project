import hmac
import time
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

SECRET_KEY = b'your-secret-key'

def index(request):
    return render(request, 'Ecoffee/qrpage.html')

def generate_params():
    timestamp = int(time.time() // 120) * 120
    signature = hmac.new(SECRET_KEY, str(timestamp).encode(), 'user111').hexdigest()
    return {'t': timestamp, 'sig': signature}
def redirect_handler(request):
    timestamp = request.GET.get('t', None)
    sig = request.GET.get('sig', None)
    
    if not timestamp or not sig:
        return HttpResponseBadRequest("Missing parameters")
    
    expected_sig = hmac.new(
        b'your-secret-key',
        str(timestamp).encode(),
        'user111'
    ).hexdigest()
    
    if not hmac.compare_digest(sig, expected_sig):
        return HttpResponse("Invalid signature", status=403)
    
    if int(time.time()) - int(timestamp) > 120:
        return HttpResponse("QR expired", status=410)
    
    return redirect('https://your-target-site.com')
