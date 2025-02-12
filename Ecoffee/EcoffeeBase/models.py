from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime


# Create your models here.
class Shop(models.Model):
    shopId = models.AutoField(primary_key=True)
    shopName = models.CharField(max_length=255, unique=True)
    numberOfVisits = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    activeCode = models.CharField(max_length=255, null=True, blank=True)


class Coffee(models.Model):
    name = models.CharField(primary_key=True, max_length=255)
    numberOrdered = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    lastOrdered = models.DateTimeField(null=True, blank=True)


class Badge(models.Model):
    badgeId = models.AutoField(primary_key=True)
    badgeName = models.CharField(unique=True, max_length=255)
    badgeDesc = models.CharField(max_length=255, null=True, blank=True)
    coffeeUntilEarned = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    """maybe information like desc or total owned? """


class User(models.Model):
    userId = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    cupsSaved = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    mostRecentShopId = models.ForeignKey(Shop, null=True, blank=True, on_delete=models.SET_NULL)
    progression = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0),MaxValueValidator(100)]
    )
    defaultBadgeId = models.ForeignKey(Badge, null=True, blank=True, on_delete=models.SET_NULL)
    lastActiveDateTime = models.DateTimeField(null=True, blank=True)


class UserShop(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    shopId = models.ForeignKey(Shop, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["userId", "shopId"], name="uniqueUserShop")
        ]
    visitAmounts = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )


class UserBadge(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    badgeId = models.ForeignKey(Badge, on_delete=models.CASCADE)
    dateTimeObtained = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["userId", "badgeId"], name="uniqueUserBadge")
        ]


def createUser(firstName, lastName):
    x = User(firstName = firstName, lastName = lastName)
    x.save()
    return


def createShop(shopName):
    x = Shop(shopName = shopName)
    x.save()
    return


def createBadge(badgeName, coffeeUntilEarned):
    x = Badge(badgeName = badgeName, coffeeUntilEarned = coffeeUntilEarned)
    x.save()
    return


def updateProgression(userId):
    userObject = User.objects.get(userId = userId)
    cupsSaved = userObject.cupsSaved
    badgeObjects = Badge.objects.order_by("coffeeUntilEarned")
    lastBadgeId = 0
    newBadgeId = 0
    if badgeObjects.count() == 0:
        return
    for badgeObject in badgeObjects:
        lastBadgeId = newBadgeId
        newBadgeId = badgeObject
        if lastBadgeId.coffeeUntilEarned <= cupsSaved and cupsSaved < newBadgeId.coffeeUntilEarned:
            updateBadge(userId, lastBadgeId, userObject)
            progression = (cupsSaved - lastBadgeId.coffeeUntilEarned) / (
                    newBadgeId.coffeeUntilEarned - lastBadgeId.coffeeUntilEarned)
            userObject.progression = round(progression * 100)
            userObject.save()
            return
    userObject.progression = 100
    userObject.save()
    updateBadge(userId, newBadgeId, userObject)
    return


def updateBadge(userId, lastBadgeId, userObject,):
    searchResult = UserBadge.objects.filter(userId=userId, badgeId=lastBadgeId)
    if not searchResult.exists():
        userObject.defaultBadgeId = lastBadgeId
        currentDateTime = datetime.now()
        x = UserBadge(userId=userId, badgeId=lastBadgeId, dateTimeObtained=currentDateTime)
        x.save()
    return


def logVisit(userId, shopId, coffeeName, visitDate, visitTime):
    userObject = User.objects.get(userId = userId)
    userObject.cupsSaved += 1
    userObject.mostRecentShopId = shopId
    userObject.save()
    updateProgression(userId)
    shopObject = Shop.objects.get(shopId = shopId)
    shopObject.numberOfVisits += 1
    shopObject.save()
    coffeeObject = Coffee.objects.get(name = coffeeName)
    coffeeObject.numberOrdered += 1
    coffeeObject.lastOrdered = datetime.combine(visitDate,visitTime)
    coffeeObject.save()
    userShopObject = UserShop.objects.get(userId = userId, shopId = shopId)
    userShopObject.visitAmounts += 1
    userShopObject.save()
    return