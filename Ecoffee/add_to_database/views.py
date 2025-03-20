from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.files.storage import default_storage
from .models import Shop, Coffee, CustomUser
from .form import *
import qrcode
from io import BytesIO
import base64
from datetime import datetime
import os
from django.conf import settings

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
            qr.add_data(str(new_shop.activeCode))
            img = qr.make_image()
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            new_shop.qr_code = base64.b64encode(buffer.getvalue()).decode()
            new_shop.save()
            return redirect('shop_owner', shop_id=new_shop.shopId)
        else:
            return render(request, 'add_shop.html', {'form': form})
    return render(request, 'add_shop.html', {'form': ShopForm()})

def shop_owner(request, shop_id):
    current_shop = Shop.objects.get(shopId=shop_id)
    top_shops = Shop.objects.order_by('-numberOfVisits')[:10]
    return render(request, 'shop_owner.html', {
        'current_shop': current_shop,
        'top_shops': top_shops,
        'qr_image': current_shop.qr_code
    })

def upload_logo(request, shop_id):
    current_shop = Shop.objects.get(shopId=shop_id)
    if request.method == 'POST':
        if 'logo' not in request.FILES:
            return render(request, 'upload_logo.html', {'error': 'Please select your file to upload', 'current_shop': current_shop})
        uploaded_file = request.FILES['logo']
        if uploaded_file.content_type not in ['image/jpeg', 'image/png']:
            return render(request, 'upload_logo.html', {'error': 'Only JPEG/PNG avible', 'current_shop': current_shop})
        if uploaded_file.size > 2 * 1024 * 1024:
            return render(request, 'upload_logo.html', {'error': 'File size over 2MB', 'current_shop': current_shop})
        file_ext = uploaded_file.name.split('.')[-1]
        file_name = f"shop_{shop_id}_logo.{file_ext}"
        file_path = os.path.join(settings.MEDIA_ROOT, 'shop_logos', file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        current_shop.logo = os.path.join('shop_logos', file_name)
        current_shop.save()
        return redirect('shop_owner', shop_id=shop_id)
    return render(request, 'upload_logo.html', {'current_shop': current_shop})

def add_coffee(request):
    if request.method=='POST':
        form=CoffeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            context = {
                'coffees':Coffee.objects.all(),
                'form':form
            }
            return render(request,'add_coffee.html',context)
        
    coffees=Coffee.objects.all()
    context={'coffees':coffees, 'form':CoffeeForm()}
    return render(request,'add_coffee.html',context)

def add_badge(request):
    if request.method=='POST':
        form=BadgeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            context = {
                'badges':Badge.objects.all(),
                'form':form
            }
            return render(request,'add_badge.html',context)
        
    badges=Badge.objects.all()
    context={'badges':badges, 'form':BadgeForm()}
    return render(request,'add_badge.html',context)
