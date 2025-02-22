from django.shortcuts import render,redirect
from EcoffeeBase.models import *
from django.utils.timezone import now
from django.db.models import Sum  


def home(request):
    today = now().date()

    # Calculate cups saved today
    cups_saved_today = User.objects.filter(lastActiveDateTime__date=today).aggregate(total=Sum('cupsSaved'))['total'] or 0

    # Set a daily goal
    daily_goal = 100  

    # Calculate progress percentage
    progress_percentage = (cups_saved_today / daily_goal) * 100 if daily_goal else 0
    progress_percentage = min(progress_percentage, 100)  # Ensure it doesn’t exceed 100%

    print("Debugging:", cups_saved_today, progress_percentage)  # Should print in terminal

    return render(request, 'homepage.html', {
        'cups_saved_today': cups_saved_today,
        'progress_percentage': round(progress_percentage, 2)  # Rounding for UI
    })


def dashboard_view(request):
    if request.user.is_authenticated:
        coffees_saved=User.objects.get(user=request.user).cupsSaved
    else:
        return redirect("login")
    
    return render(request, 'dashboard.html',{"coffee_code":coffees_saved})


