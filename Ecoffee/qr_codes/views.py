from django.shortcuts import render,redirect
from django.http import HttpResponse
from EcoffeeBase.models import *
from datetime import datetime
def receive_code(request):
    code = str(request.GET.get('code', 'No code provided'))
    try:
        #find part of the code which is relavent to the shop/coffee
        shop=Shop.objects.get(activeCode=code)
        coffee=Coffee.objects.get(activeCode=code)
        coffee.numberOrdered+=1
        coffee.lastOrdered=datetime.now()
        shop.numberOfVisits+=1
        shop.save()
        coffee.save()
        if request.user.is_authenticated:
            try:
                username=request.user.username
                user=User.objects.get(userId=username)
                user.cupsSaved+=1
                user.mostRecentShopId=shop.shopId
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