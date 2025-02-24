from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class Shop(models.Model):
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
    badge_image = models.CharField(max_length=255, default='')  # store link instead of actual image
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
                fields=["user", "shop_id"], name="unique_user_shop")
        ]


class UserBadge(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    badge_id = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_time_obtained = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "badge_id"], name="unique_user_badge")
        ]