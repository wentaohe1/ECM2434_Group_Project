from django.shortcuts import render,redirect
from django.http import HttpResponse
from EcoffeeBase.models import *
from datetime import datetime
from .form import CoffeeForm


def receive_code(request):
    if request.method=='POST':
        form=CoffeeForm(request.POST)
        if form.is_valid():
            coffee=form.cleaned_data['coffee_selected']
            coffee.numberOrdered+=1
            coffee.lastOrdered=datetime.now()
            code = str(request.GET.get('code', 'No code provided'))
            try:
                #find part of the code which is relavent to the shop
                shop_code=read_shop_code(code,4)#for now, first 4 letters, allows for expansion later.
                print(shop_code)
                shop=Shop.objects.get(activeCode=int(shop_code))
                shop.numberOfVisits+=1
                if request.user.is_authenticated:
                    try:
                        username=request.user #Updates information relevant to the users order.
                        user=CustomUser.objects.get(user=username)
                        user.cupsSaved+=1
                        user.mostRecentShopId=shop
                        user.lastActiveDateTime=datetime.now()
                        #need to run a trigger to check if the badge needs to be updated.
                        user.save()
                        shop.save()
                        coffee.save() #saves after everything is confirmed okay, changes will rollback (by default after a request has returned) if not
                        return redirect('home')
                    except CustomUser.DoesNotExist:
                        return redirect('register')
                else:
                    #user not logged in has to login/create account
                    return redirect('login')
            except Shop.DoesNotExist:
                return redirect('home')
    
    coffees=Coffee.objects.all()
    context={'coffees':coffees, 'form':CoffeeForm()}
    return render(request,'add_coffee.html',context)
        


def read_shop_code(code,number_of_letters):
    return code[:number_of_letters]
