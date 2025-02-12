from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Shop(models.Model):
    shopId = models.AutoField(primary_key=True)
    shopName = models.CharField(max_length=255, unique=True)
    numberOfVisits = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    activeCode = models.CharField(max_length=255)


class Coffee(models.Model):
    name = models.CharField(max_length=255, unique=True)
    numberOrdered = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    lastOrdered = models.DateTimeField(null=True, blank=True)


class Badge(models.Model):
    badgeId = models.AutoField(primary_key=True)
    coffeeUntilEarned = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    """maybe information like desc or total owned? """


class User(models.Model):
    userId = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    cupsSaved = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    mostRecentShopId = models.ForeignKey(
        Shop,
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    progression = models.IntegerField(
        validators=[
            MinValueValidator(0), 
            MaxValueValidator(100)
        ]
    )
    defaultBadgeId = models.ForeignKey(
        Badge, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    lastActiveDateTime = models.DateTimeField(null=True, blank=True)


class UserShop(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    shopId = models.ForeignKey(Shop, on_delete=models.CASCADE)
    visitAmounts = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["userId", "shopId"], 
                name="uniqueUserShop"
            )
        ]


class UserBadge(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    badgeId = models.ForeignKey(Badge, on_delete=models.CASCADE)
    owned = models.BooleanField(default=False)
    dateTimeObtained = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["userId", "badgeId"], 
                name="uniqueUserBadge"
            )
        ]

