from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from EcoffeeBase.models import *
from django.utils.timezone import now
from django.db.models import Sum
from django.templatetags.static import static
from EcoffeeBase.forms import ProfileImageForm, ChangeUserDetailsForm
from django.http import HttpResponseForbidden


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
        progress_percentage, 100)  # Ensure it doesn't exceed 100%
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
    })


def dashboard_view(request):
    if request.user.is_authenticated:  # only accessible if logged in
        request_user = CustomUser.objects.get(user=request.user)
        percentage_above_average = calculate_percentage_above_average(
            request_user)
        negative = False
        if percentage_above_average < 0:
            negative = True
            percentage_above_average = -percentage_above_average
        coffees_saved = request_user.cups_saved
        most_visited_shop = UserShop.objects.filter(
            user=request_user).order_by('-visit_amounts').first()
        top_three_earned_badges = reversed(UserBadge.objects.filter(
            user=request_user).all().order_by('-badge_id__coffee_until_earned')[:3])

        if request_user.default_badge_id != None:  # retreive the image and next badge from the database
            user_badge = str(request_user.default_badge_id.badge_image)
            next_badge = get_next_badge(request_user)
        else:
            user_badge = 'defaultbadge.png'  # default values
            next_badge = None
        # checking that the database has data and the user has a badge to display
        if next_badge is not None and user_badge != '':
            coffees_to_next_badge = int(
                next_badge.coffee_until_earned)-int(request_user.cups_saved)
            progress = 100-round((coffees_to_next_badge /
                                  int(next_badge.coffee_until_earned)*100))
        else:
            # very large number (unachievable)
            coffees_to_next_badge = 1000000000
            progress = 100
            if user_badge=='defaultbadge.png':
                progress=0
                try:
                    coffees_to_next_badge=Badge.objects.order_by('coffee_until_earned').first().coffee_until_earned
                except AttributeError:
                    progress=100
                    coffees_to_next_badge=1000000000




    else:
        return redirect("login")  # if logged out, send to login page

    return render(request, 'dashboard.html', {
        "coffees_saved": coffees_saved,
        "money_saved": str(round(int(coffees_saved)*0.2, 2)),
        "badge_file": user_badge,
        "most_popular_shop": Shop.objects.order_by('-number_of_visits').first(),
        "progress": progress,
        "coffees_to_next_badge": coffees_to_next_badge,
        "most_visited_shop": most_visited_shop,
        "top_three_badges": top_three_earned_badges,
        "percentage_above_average": percentage_above_average,
        "negative": negative,
    })

# orders badges and then returns the first badge that has a higher requirement than the cups the user has saved


def get_next_badge(request_user):
    current_badge = request_user.default_badge_id
    if current_badge is None:
        return None

    ordered_badges = Badge.objects.order_by('coffee_until_earned')

    for badge in ordered_badges:
        if badge.coffee_until_earned > current_badge.coffee_until_earned:
            return badge

    return None


def welcome(request):
    return render(request, 'welcome.html')
# (sprint2) Ensure users without a badge get a default badge


def calculate_percentage_above_average(request_user):
    all_users = CustomUser.objects.all()
    total = 0
    for user in all_users:
        total += user.cups_saved
    if total == 0:  # if no one has saved a cup, return 1
        return 0
    average = (total/len(all_users))

    result = (request_user.cups_saved-average)/(total/len(all_users))*100
    return result


# settings view
def settings_view(request):
    user = request.user.customuser
    if request.method == 'POST':
        picture_form = ProfileImageForm(instance=user)
        user_form = ChangeUserDetailsForm(instance=request.user)
        if 'picture_form_submit' in request.POST:
            picture_form = ProfileImageForm(
                request.POST, request.FILES, instance=user)
            if picture_form.is_valid():
                picture_form.save()
                return redirect('settings')
            else:
                context = {
                    'picture_form': picture_form,
                    'user_form': user_form
                }
                return render(request, 'settings.html', context)
        elif 'user_form_submit' in request.POST:
            user_form = ChangeUserDetailsForm(
                request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                return redirect('login')
            else:
                print("Form errors:", user_form.errors)
                context = {
                    'picture_form': picture_form,
                    'user_form': user_form
                }
                return render(request, 'settings.html', context)

    context = {'user_form': ChangeUserDetailsForm(
        instance=request.user), 'picture_form': ProfileImageForm(instance=user)}
    return render(request, 'settings.html', context)


@login_required
def delete_user(request):
    if request.method == "POST":
        user = request.user
        try:
            custom_user = CustomUser.objects.get(user=user)
            UserShop.objects.filter(user=custom_user).delete()
            UserBadge.objects.filter(user=custom_user).delete()
            ShopUser.objects.filter(user=user).delete()
            custom_user.delete()
        except CustomUser.DoesNotExist:
            pass

        user.delete()

        return redirect('login')
    return HttpResponseForbidden("Invalid request method")
