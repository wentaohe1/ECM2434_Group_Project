from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegistrationForm;
from EcoffeeBase.models import *
from django.utils.timezone import now

def login_user(request):
    if request.user.is_authenticated: #if the user is already authenticated, redirect them to the home page
        return redirect('home')
    
    if request.method=="POST":
        username=request.POST["username"]
        password=request.POST["password"]
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            current_user = CustomUser.objects.get(user = request.user)
            time = now()
            current_user.last_active_date_time = time
            streak_day_difference = time.date() - current_user.streak_start_day
            if streak_day_difference.days == current_user.streak:
                current_user.streak += 1
            elif streak_day_difference.days >= current_user.streak:
                current_user.streak = time.date()
            current_user.save()
            return redirect('home')  # Redirect to the home page after successful login
        else:
            messages.error(request, "There was an error logging in. Try again.") #Error if login failed.
            return redirect('login')

    response = render(request,'authenticate/login.html', {})
    response['Cache-Control']='no-store' #Prevent caching of login page, prevents bugs.
    response['Pragma']='no-cache'
    response['Expires']='0'
    return response


def logout_user(request):
    logout(request)
    messages.success(request, ("Logout successful"))
    return redirect('login')



def register_user(request):
    if request.method=="POST":
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            user=form.save()
            username=form.cleaned_data['username']
            password=form.cleaned_data['password1']
            user=authenticate(username=username, password=password)

            if user:
                login(request, user)
                messages.success(request,"Registration Successful")
                return redirect('home')
            else:
                messages.error(request,"Authentication failed. Please try again.")
                return redirect('register')

    else:
        form = UserRegistrationForm()

    return render(request,'authenticate/register_user.html',{'form': form})

