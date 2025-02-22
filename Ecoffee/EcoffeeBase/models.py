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


class Coffee(models.Model):
    name = models.CharField(max_length=255, unique=True)
    number_ordered = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0
    )
    last_ordered = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Badge(models.Model):
    badge_id = models.AutoField(primary_key=True)
    coffee_until_earned = models.IntegerField(
        validators=[MinValueValidator(0)],
        unique=True
    )
    """maybe information like desc or total owned? """


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cups_saved = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    most_recent_shop_id = models.ForeignKey(
        Shop, null=True, blank=True, on_delete=models.SET_NULL)
    default_badge_id = models.ForeignKey(
        Badge, null=True, blank=True, on_delete=models.SET_NULL)
    last_active_date_time = models.DateTimeField(null=True, blank=True)


class UserShop(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    shop_id = models.ForeignKey(Shop, on_delete=models.CASCADE)
    visit_amounts = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "shopId"], name="uniqueUserShop")
        ]


class UserBadge(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    badge_id = models.ForeignKey(Badge, on_delete=models.CASCADE)
    owned = models.BooleanField(default=False)
    date_time_obtained = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "badgeId"], name="uniqueUserBadge")
        ]


def create_user(first_name, last_name):
    x = User(firstName=first_name, lastName=last_name)
    x.save()
    return


def create_shop(shop_name):
    x = Shop(shopName=shop_name)
    x.save()
    return


def create_badge(badge_name, coffee_until_earned):
    x = Badge(badgeName=badge_name, coffeeUntilEarned=coffee_until_earned)
    x.save()
    return


def update_progression(user_id):
    user_object = User.objects.get(user_id=user_id)
    cups_saved = user_object.cupsSaved
    badge_objects = Badge.objects.order_by("coffeeUntilEarned")
    last_badge_id = 0
    new_badge_id = 0
    if badge_objects.count() == 0:
        return
    for badge_object in badge_objects:
        last_badge_id = new_badge_id
        new_badge_id = badge_object
        if last_badge_id.coffeeUntilEarned <= cups_saved and cups_saved < new_badge_id.coffeeUntilEarned:
            update_badge(user_id, last_badge_id, user_object)
            progression = (cups_saved - last_badge_id.coffeeUntilEarned) / (
                new_badge_id.coffeeUntilEarned - last_badge_id.coffeeUntilEarned)
            user_object.progression = round(progression * 100)
            user_object.save()
            return
    user_object.progression = 100
    user_object.save()
    update_badge(user_id, new_badge_id, user_object)
    return


def update_badge(user_id, last_badge_id, user_object,):
    search_result = UserBadge.objects.filter(user_id=user_id, badgeId=last_badge_id)
    if not search_result.exists():
        user_object.defaultBadgeId = last_badge_id
        current_date_time = datetime.now()
        x = UserBadge(userId=user_id, badgeId=last_badge_id,
                      dateTimeObtained=current_date_time)
        x.save()
    return


def log_visit(user_id, shop_id, coffee_name, visit_date, visit_time):
    user_object = User.objects.get(user_id=user_id)
    user_object.cupsSaved += 1
    user_object.mostRecentShopId = shop_id
    user_object.save()
    update_progression(user_id)
    shop_object = Shop.objects.get(shop_id=shop_id)
    shop_object.numberOfVisits += 1
    shop_object.save()
    coffee_object = Coffee.objects.get(name=coffee_name)
    coffee_object.numberOrdered += 1
    coffee_object.lastOrdered = datetime.combine(visit_date, visit_time)
    coffee_object.save()
    user_shop_object = UserShop.objects.get(user_id=user_id, shop_id=shop_id)
    user_shop_object.visitAmounts += 1
    user_shop_object.save()
    return
