from django.shortcuts import render,redirect
from EcoffeeBase.models import *
from .form import *

def add_new_data(request):
    if request.method=='POST':
        if 'shop_form_submit' in request.POST:
            print("here")
            shop_form=ShopForm(request.POST)
            if shop_form.is_valid():
                shop_form.save()
                return redirect('home')
            else:
                context = {
                    'shop_form':shop_form,
                    'badge_form':BadgeForm()
                }
                return render(request,'add_new_data.html',context)
        elif 'badge_form_submit' in request.POST:
            badge_form=BadgeForm(request.POST)
            if badge_form.is_valid():
                badge_form.save()
                return redirect('home')
            else:
                context = {
                    'shop_form':ShopForm(),
                    'badge_form':badge_form
                }
                return render(request,'add_new_data.html',context)
    else:
        context={'badge_form':BadgeForm(), 'shop_form':ShopForm()}
        return render(request,'add_new_data.html',context)
            






