from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.files.storage import default_storage
from EcoffeeBase.models import Shop,CustomUser
from .form import *
import qrcode
from io import BytesIO
import base64
from datetime import datetime
import os
from django.conf import settings
from django.http import HttpResponseForbidden
from functools import wraps

def shop_owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            shop_user = ShopUser.objects.get(user=request.user)
        except ShopUser.DoesNotExist:
            return HttpResponseForbidden("You do not have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@shop_owner_required
def add_shop(request):
    if request.method == 'POST':
        form = ShopForm(request.POST)
        if form.is_valid():
            new_shop = form.save()
            qr = qrcode.QRCode(
                version=1,
                box_size=10,
                border=4,
            )
            qr.add_data(str(new_shop.active_code))
            img = qr.make_image()
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            new_shop.qr_code = base64.b64encode(buffer.getvalue()).decode()
            new_shop.save()
            return redirect('shop_owner', shop_id=new_shop.shop_id)
        else:
            return render(request, 'add_shop.html', {'form': form})
    return render(request, 'add_shop.html', {'form': ShopForm()})


@shop_owner_required
def shop_owner(request, shop_id):
    current_shop = Shop.objects.get(shop_id=shop_id)
    top_shops = Shop.objects.order_by('-number_of_visits')[:10]
    return render(request, 'shop_owner.html', {
        'current_shop': current_shop,
        'top_shops': top_shops,
        'qr_image': current_shop.qr_code
    })


@shop_owner_required
def upload_logo(request,shop_id):
    shop=Shop.objects.get(shop_id=shop_id)
    if request.method == 'POST':
        logo_form = LogoForm(request.POST, request.FILES, instance=shop)
        if logo_form.is_valid():
            logo_form.save()
            return redirect('home')
        else:
            context={'logo_form':logo_form}
            return render(request,'upload_logo.html',context)
    else:
        return render(request,'upload_logo.html', {'current_shop': shop})

