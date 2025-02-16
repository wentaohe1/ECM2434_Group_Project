from django.shortcuts import render,redirect
from EcoffeeBase.models import *
from .form import *

def add_shop(request):
    if request.method=='POST':
        form=ShopForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            context = {
                'shops':Shop.objects.all(),
                'form':form
            }
            return render(request,'add_shop.html',context)   
    shops=Shop.objects.all()
    context={'shops':shops, 'form':ShopForm()}
    return render(request,'add_shop.html',context)

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
