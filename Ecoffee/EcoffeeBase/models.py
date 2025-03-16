"""
This module contains the databases amd their attributes. The attributes are queried from and to this database.
All the tables here represents the entire database section (not including the username and password table which is done
elsewhere separately to provide more security and protection). The tables are created using the .model framework form
django that uses SQLite.

Original made by Lok Sang Kee
Edited and improved by Project Team A
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now


class Shop(models.Model):
    """
    Represents a shop object.

    shop_id: Auto assigned ID of shop. It is a primary key.
    shop_name: Name of the shop. It is filled in when creating shop accounts.
    number_of_visits: The total number of visits of a shop. It increments by one every time someone logs a visit to
    the shop.
    active_code: The current active code of the shop. It helps to check which shop did a user visited. It is extracted
    from the qr code. It is created in the shop account.
    """
    shop_id = models.AutoField(primary_key=True)
    shop_name = models.CharField(max_length=255, unique=True)
    number_of_visits = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0
    )
    active_code = models.CharField(max_length=255)


class Badge(models.Model):
    """
    Represents a badge object.

    badge_id: Auto assigned ID of badge. It is a primary key.
    coffee_until_earned: The total number of coffees required to get the badge. It is made when the badge is created.
    badge_image: The icon that will represent the badge on the website. It is made when the badge is created.
    """
    badge_id = models.AutoField(primary_key=True)
    coffee_until_earned = models.IntegerField(
        validators=[MinValueValidator(0)],
        unique=True
    )
    # store link instead of actual image
    badge_image = models.CharField(max_length=255, default='defaultbadge.png')


class CustomUser(models.Model):
    """
    Represents a user object (basic user with no special permissions).

    user_id(hidden): An ID created and added automatically when the table is created and when a new record is added.
    It is not used in the codes. It is a primary key.
    user: The username of a user. It is created when the user registers. It is unique, so it is used as a
    representation of the table in other ports of the codes.
    cups_saved: The number of cups a user has saved. It increments by one every time the user logs a visit to a
    partnering coffee shop.
    most_recent_shop_id: The ID of the most recently visited shop of the user. The ID is also a primary key in the
    Shop table. It is renewed when the user logs a visit.
    default_badge_id: The ID of the badge currently equipped by the user. This is currently changed automatically
    whenever a user unlock a new badge with more coffee_until_earned. It may be changed later to allow user to change
    the badges themselves. The attribute is also a primary key of the Badge table.
    last_active_date_time: The date and time of the most recent logged visit of the user. It is updated when the user
    logs a new visit.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cups_saved = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    most_recent_shop_id = models.ForeignKey(
        Shop, null=True, blank=True, on_delete=models.SET_NULL)
    default_badge_id = models.ForeignKey(
        Badge, null=True, blank=True, on_delete=models.SET_NULL)
    last_active_date_time = models.DateTimeField(auto_now_add=True)
    streak = models.IntegerField(default=1)
    streak_start_day = models.DateField(default=now)


class UserShop(models.Model):
    """
    Represents a user-shop relation and stores the number of visits of each user to each shop.

    user: The username of the user participating in the relation. It is created when a user logs a visit to a shop he
    has not logged before. It joins with shop_id to form a composite primary key. The attribute is a primary key of
    the CustomUser table.
    shop_id: The ID of the shop participating in the relation. It is created when a user logs a visit to a shop he
    has not logged before. It joins with user to form a composite primary key. The attribute is a primary key of the
    Shop table.
    visit_amounts: The number of times a user has logged a visit to a specific shop. It is incremented by one when the
    user logs a new visit to the shop.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    shop_id = models.ForeignKey(Shop, on_delete=models.CASCADE)
    visit_amounts = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    class Meta:
        """
        This is for combining user and shop_id to form a composite key.
        """
        constraints = [
            models.UniqueConstraint(
                fields=["user", "shop_id"], name="unique_user_shop")
        ]


class UserBadge(models.Model):
    """
    Represents a user-badge relation and stores the date and time when each user obtains each badge. Only the badges
    that are owned by a user will be added to the table.

    user: The username of the user participating in the relation. It is created when a user earns a badge he has not
    obtained before. It joins with badge_id to form a composite primary key. The attribute is a primary key of
    the CustomUser table.
    badge_id: The ID of the badge participating in the relation. It is created when a user earns a badge he has not
    obtained before. It joins with user to form a composite primary key. The attribute is a primary key of the
    Badge table.
    date_time_obtained: The date and time when a user obtains a specific badge.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    badge_id = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_time_obtained = models.DateTimeField(null=True, blank=True)

    class Meta:
        """
        This is for combining user and badge_id to form a composite key.
        """
        constraints = [
            models.UniqueConstraint(
                fields=["user", "badge_id"], name="unique_user_badge")
        ]
