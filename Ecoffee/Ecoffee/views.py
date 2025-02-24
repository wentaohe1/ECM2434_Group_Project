from django.shortcuts import render,redirect
from EcoffeeBase.models import *
from django.utils.timezone import now
from django.db.models import Sum  

def home(request):
    today = now().date()

    # Calculate cups saved today
    cups_saved_today = CustomUser.objects.filter(last_active_date_time=today).aggregate(total=Sum('cups_saved'))['total'] or 0
    total_cups_saved=Shop.objects.all().aggregate(total=Sum('number_of_visits'))['total'] or 0
    # Set a daily goal
    daily_goal = 100  
    # Calculate progress percentage
    progress_percentage = (cups_saved_today / daily_goal) * 100 if daily_goal else 0
    progress_percentage = min(progress_percentage, 100)  # Ensure it doesn’t exceed 100%

    print("Debugging:", cups_saved_today, progress_percentage)  # Should print in terminal
    request_user=CustomUser.objects.get(user=request.user)
    personal_cups_saved=request_user.cupsSaved
    top_10_users=CustomUser.objects.all().order_by('-cups_saved')[:10] #top 10 users ordered in descending order
    top_5_shops=Shop.objects.all().order_by('-number_of_visits')[:5]
    return render(request, 'homepage.html', {
        'cups_saved_today': cups_saved_today,
        'progress_percentage': round(progress_percentage, 2), # Rounding for UI
        'top_10_users':top_10_users,
        'top_5_shops':top_5_shops,
        'total_cups_saved':total_cups_saved,
        'personal_cups_saved':personal_cups_saved,
    })


def dashboard_view(request):
    if request.user.is_authenticated:
        request_user=CustomUser.objects.get(user=request.user)
        coffees_saved=request_user.cups_saved
        user_badge='images/'+str(request_user.default_badge_id.badge_image)
        next_badge=get_next_badge(request_user)
        if next_badge!=None:
            coffees_to_next_badge=int(next_badge.coffee_until_earned)-int(request_user.default_badge_id.coffee_until_earned)
            progress=round(coffees_to_next_badge/int(next_badge.coffee_until_earned)*100)
        else:
            coffees_to_next_badge=1000000000
            progress=100

    else:
        return redirect("login")
    
    return render(request, 'dashboard.html',{
        "coffees_saved":coffees_saved,
        "money_saved":str(round(int(coffees_saved)*0.2,2)),
        "badge_file":str(user_badge),
        "most_popular_shop":Shop.objects.order_by('-number_of_visits').first(),
        "progress":progress,
        "coffees_to_next_badge":coffees_to_next_badge
        })

def get_next_badge(request_user):
    current_badge=request_user.default_badge_id
    ordered_badges=Badge.objects.order_by('coffee_until_earned')

    for badge in ordered_badges:
        if badge.coffee_until_earned>current_badge.coffee_until_earned:
            return badge