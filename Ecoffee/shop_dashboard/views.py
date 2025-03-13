# shop_dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from EcoffeeBase.models import Shop
from .models import ShopLogo
from .forms import LogoUploadForm
import qrcode
import hmac
import time
from io import BytesIO
import base64


SECRET_KEY = b'coffee-secret-key-2024'  

def generate_params():
    timestamp = int(time.time() // 120) * 120
    signature = hmac.new(SECRET_KEY, str(timestamp).encode(), 'sha256').hexdigest()
    return {'t': timestamp, 'sig': signature}

@login_required
def shop_owner_dashboard(request):
    # 假设用户与店铺关联（需根据实际模型调整）
    shop = request.user.shop

    params = generate_params()
    qr_url = f"{settings.SITE_URL}/receive_code/?code={shop.active_code}&t={params['t']}&sig={params['sig']}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    # get dashoard information
    top_shops = Shop.objects.order_by('-number_of_visits')[:10]

    return render(request, 'shop_owner.html', {
        'qr_image': qr_base64,
        'top_shops': top_shops,
        'current_shop': shop
    })

@login_required
def upload_shop_logo(request):
    shop = request.user.shop
    if request.method == 'POST':
        form = LogoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Delete old Logo
            ShopLogo.objects.filter(shop=shop).delete()
            # Save new Logo
            new_logo = form.save(commit=False)
            new_logo.shop = shop
            new_logo.save()
            return redirect('shop-dashboard')
    else:
        form = LogoUploadForm()
    return render(request, 'upload_logo.html', {'form': form})
