from django.shortcuts import render,redirect
from django.http import HttpResponse
from EcoffeeBase.models import *
from datetime import datetime
def receive_code(request):
    code = str(request.GET.get('code', 'No code provided'))
    try:
        shop_name=code[:4]
        coffee_code=code[4:8]
        shop_code=code[8:12]


        #find part of the code which is relavent to the shop/coffee
        shop=Shop.objects.get(activeCode=shop_code)
        coffee=Coffee.objects.get(name=coffee_code)
        coffee.numberOrdered+=1
        coffee.lastOrdered=datetime.now()
        shop.numberOfVisits+=1
        shop.save()
        coffee.save()
        if request.user.is_authenticated:
            try:
                username=request.user
                user=User.objects.get(user=username)
                user.cupsSaved+=1
                user.mostRecentShopId=shop
                user.progression+=1
                user.lastActiveDateTime=datetime.now()
                #need to run a trigger to check if the badge needs to be updated.
                user.save()
            except User.DoesNotExist:
                return redirect('home')
        else:
            #user not logged in has to login/create account
            return redirect('login')
        


    except Shop.DoesNotExist:
        return redirect('home')
    

    
    return HttpResponse(f"Received code: {code}")