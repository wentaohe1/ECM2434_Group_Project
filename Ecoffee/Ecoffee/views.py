from django.shortcuts import render, redirect
from EcoffeeBase.models import *
from django.utils.timezone import now
from django.db.models import Sum
from django.templatetags.static import static


def home(request):
    today = now().date()

    # Calculate cups saved today
    cups_saved_today = CustomUser.objects.filter(
        last_active_date_time=today).aggregate(total=Sum('cups_saved'))['total'] or 0
    total_cups_saved = Shop.objects.all().aggregate(
        total=Sum('number_of_visits'))['total'] or 0
    # Set a daily goal
    daily_goal = 100
    if (request.user.is_authenticated):  # only get data from database if the user is logged in
        request_user = CustomUser.objects.get(user=request.user)
        personal_cups_saved = request_user.cups_saved
        if request_user.default_badge_id != None:
            user_badge = 'images/' + \
                str(request_user.default_badge_id.badge_image)
        else:
            user_badge = ''  # prevent crashing from empty database
    else:
        personal_cups_saved = ''  # set as default values if not logged in
        user_badge = ''
    # Calculate progress percentage
    progress_percentage = (cups_saved_today / daily_goal) * \
        100 if daily_goal else 0
    progress_percentage = min(
        progress_percentage, 100)  # Ensure it doesn’t exceed 100%
    # Function to determine user badge path
    top_10_users = CustomUser.objects.all().order_by(
        '-cups_saved')[:10]  # top 10 users ordered in descending order
    top_5_shops = Shop.objects.all().order_by(
        '-number_of_visits')[:5]  # top 5 stores in decending order
    return render(request, 'homepage.html', {
        'cups_saved_today': cups_saved_today,
        # Rounding for UI
        'progress_percentage': round(progress_percentage, 2),
        'top_10_users': top_10_users,
        'top_5_shops': top_5_shops,
        'total_cups_saved': total_cups_saved,
        'personal_cups_saved': personal_cups_saved,
        'user_badge': user_badge,
    })


def dashboard_view(request):
    if request.user.is_authenticated:  # only accessible if logged in
        request_user = CustomUser.objects.get(user=request.user)
        coffees_saved = request_user.cups_saved
        if request_user.default_badge_id != None:  # retreive the image and next badge from the database
            user_badge = 'images/' + \
                str(request_user.default_badge_id.badge_image)
            next_badge = get_next_badge(request_user)
        else:
            user_badge = ''  # default values
            next_badge = ''
        # checking that the database has data and the user has a badge to display
        if next_badge != None and user_badge != '':
            coffees_to_next_badge = int(
                next_badge.coffee_until_earned)-int(request_user.cups_saved)
            progress = 100-round((coffees_to_next_badge /
                                 int(next_badge.coffee_until_earned)*100))
        else:
            # very large number (unachievable)
            coffees_to_next_badge = 1000000000
            progress = 100

    else:
        return redirect("login")  # if logged out, send to login page

    return render(request, 'dashboard.html', {
        "coffees_saved": coffees_saved,
        "money_saved": str(round(int(coffees_saved)*0.2, 2)),
        "badge_file": str(user_badge),
        "most_popular_shop": Shop.objects.order_by('-number_of_visits').first(),
        "progress": progress,
        "coffees_to_next_badge": coffees_to_next_badge
    })

# orders badges and then returns the first badge that has a higher requirement thant he cups the user has saved


def get_next_badge(request_user):
    current_badge = request_user.default_badge_id
    ordered_badges = Badge.objects.order_by('coffee_until_earned')

    for badge in ordered_badges:
        if badge.coffee_until_earned > current_badge.coffee_until_earned:
            return badge


def welcome(request):
    return render(request, 'welcome.html')
# (sprint2) Ensure users without a badge get a default badge
