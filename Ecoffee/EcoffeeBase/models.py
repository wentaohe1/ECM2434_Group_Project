from django.db import models
from django.contrib import admin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from datetime import datetime

class Shop(models.Model):
    shop_id = models.AutoField(primary_key=True)
    shop_name = models.CharField(max_length=255, unique=True)
    number_of_visits = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0
    )
    active_code = models.CharField(max_length=255)
    shop_id = models.AutoField(primary_key=True)
    shop_name = models.CharField(max_length=255, unique=True)
    number_of_visits = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0
    )
    active_code = models.CharField(max_length=255)


class Badge(models.Model):
    badge_id = models.AutoField(primary_key=True)
    coffee_until_earned = models.IntegerField(
        validators=[MinValueValidator(0)],
        unique=True
    )
    badge_image = models.CharField(max_length=255, default='defaultbadge.png')  # store link instead of actual image
    """maybe information like desc or total owned? """


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cups_saved = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    most_recent_shop_id = models.ForeignKey(Shop, null=True, blank=True, on_delete=models.SET_NULL)
    default_badge_id = models.ForeignKey(Badge, null=True, blank=True, on_delete=models.SET_NULL)
    last_active_date_time = models.DateTimeField(null=True, blank=True)


class UserShop(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    shop_id = models.ForeignKey(Shop, on_delete=models.CASCADE)
    visit_amounts = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "shop_id"], name="unique_user_shop")
        ]


class UserBadge(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    badge_id = models.ForeignKey(Badge, on_delete=models.CASCADE)
    owned = models.BooleanField(default=False)
    date_time_obtained = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "badge_id"], name="unique_user_badge")
        ]


def create_user(first_name, last_name):
    x = User(first_name = first_name, last_name = last_name)
    x.save()
    return


def create_shop(shop_name):
    x = Shop(shop_name = shop_name)
    x.save()
    return


def create_badge(badge_name, coffee_until_earned):
    x = Badge(badge_name = badge_name, coffee_until_earned = coffee_until_earned)
    x.save()
    return


def update_progression(user):
    user_object = CustomUser.objects.get(user = user)
    cups_saved = user_object.cups_saved
    badge_objects = Badge.objects.order_by("coffee_until_earned")
    last_badge_id = 0
    new_badge_id = 0
    if badge_objects.count() == 0:
        return
    for badge_object in badge_objects:
        last_badge_id = new_badge_id
        new_badge_id = badge_object
        if last_badge_id.coffee_until_earned <= cups_saved and cups_saved < new_badge_id.coffee_until_earned:
            update_badge(user, last_badge_id, user_object)
            progression = (cups_saved - last_badge_id.coffee_until_earned) / (
                    new_badge_id.coffee_until_earned - last_badge_id.coffee_until_earned)
            user_object.progression = round(progression * 100)
            user_object.save()
            return
    user_object.progression = 100
    user_object.save()
    update_badge(user, new_badge_id, user_object)
    return


def update_badge(user, last_badge_id, user_object,):
    search_result = UserBadge.objects.filter(user=user, badge_id=last_badge_id)
    if not search_result.exists():
        user_object.default_badge_id = last_badge_id
        current_date_time = datetime.now()
        x = UserBadge(user=user, badge_id=last_badge_id, dateT_time_obtained=current_date_time)
        x.save()
    return


def log_visit(user, shop_id, coffee_name, visit_date, visit_time):
    user_object = CustomUser.objects.get(user = user)
    user_object.cups_saved += 1
    user_object.most_recent_shop_id = shop_id
    user_object.save()
    update_progression(user)
    shop_object = Shop.objects.get(shopId = shopId)
    shop_object.number_of_visits += 1
    shop_object.save()
    coffee_object = Coffee.objects.get(name = coffee_name)
    coffee_object.number_ordered += 1
    coffee_object.last_ordered = datetime.combine(visit_date,visit_time)
    coffee_object.save()
    user_shop_object = UserShop.objects.get(user = user, shop_id = shop_id)
    user_shop_object.visit_amounts += 1
    user_shop_object.save()
    return