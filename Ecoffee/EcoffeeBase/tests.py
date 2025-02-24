from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from datetime import timedelta
from django.utils.timezone import now
from EcoffeeBase.models import Shop, User, UserShop, Badge, UserBadge, Coffee
from EcoffeeBase.views import log_visit

class DataBaseTests(TestCase):

    def setUp(self):
        '''Sets up a DB with test objects and a simulated POST request'''

        self.shop = Shop.objects.create(shopName = 'New Shop', activeCode = '123', numberOfVisits = 0)
        self.user = User.objects.create(firstName = 'John', lastName = 'Smith', cupsSaved = 0, progression = 0)
        self.coffee = Coffee.objects.create(name = 'espresso', numberOrdered = 0)

        # Initialises badges: different thresholds enable user.defaultBadgeId testing
        self.badge_1 = Badge.objects.create(coffeeUntilEarned = 2)
        self.badge_2 = Badge.objects.create(coffeeUntilEarned = 3)

        # Simulates recieving a POST request
        self.request = self.client.post(reverse('log_visit'), {'userId': self.user.userId, 'shopId': self.shop.shopId, 'coffeeName': self.coffee.name})

    def test_shop_registers_visit(self):
        '''Tests log_visit updates Shop attributes to reflect user's visit'''

        this_shop = Shop.objects.get(shopId = self.shop.shopId)

        self.assertEqual(this_shop.numberOfVisits, 1, 'Shop vist count should increment on visit')

    def test_user_registers_visit(self):
        '''Tests log_visit updates User attributes to reflect a shop visit'''

        this_user = User.objects.get(userId = self.user.userId)

        self.assertEqual(this_user.mostRecentShopId.shopId, self.shop.shopId, 'The visited shop should be set as the user\'s most recent shop')

        self.assertEqual(this_user.progression, 1, 'User progression should increment on visit')

        self.assertEqual(this_user.cupsSaved, 1, 'User\'s cups saved count should increment on visit')

        self.assertAlmostEqual(this_user.lastActiveDateTime, now(), delta = timedelta(seconds = 1))

    def test_user_shop_registers_visit(self):
        '''Tests log_visit updates UserShop attributes to reflect a user's visit'''

        try:
            this_userShop = UserShop.objects.get(userId = self.user.userId, shopId = self.shop.shopId)
        except UserShop.DoesNotExist:
            print("UserShop instance should be created for the user - shop pair")

        self.assertEqual(this_userShop.userId.userId, self.user.userId, 'The UserShop instance should reference the correct parent User')

        self.assertEqual(this_userShop.shopId.shopId, self.shop.shopId, 'The UserShop instance should reference the correct parent Shop')

        self.assertEqual(this_userShop.visitAmounts, 1, 'UserShop vist count should increment on visit')

    def test_user_badge_registers_visit(self):
        '''Tests log_visit updates UserBadge attributes to reflect a user's visit'''

        # Simulates a second request
        log_visit(self.request.wsgi_request)

        this_badge = Badge.objects.get(badgeId = self.badge_1.badgeId)
        this_user = User.objects.get(userId = self.user.userId)

        try:
            user_badge = UserBadge.objects.get(badgeId = this_badge.badgeId, userId = self.user.userId)
        except UserBadge.DoesNotExist:
            print("UserBadge instance should be created for the user - badge pair")

        # Tests user fields updated
        self.assertEqual(this_user.progression, 0, 'User progression should reset on earning a badge')

        self.assertEqual(this_user.defaultBadgeId.badgeId, this_badge.badgeId, 'Initial earned badge should be set as the User\'s default badge')

        # Tests user_badge fields updated
        self.assertEqual(user_badge.owned, True, 'Badge ownership status should be True once earned')

        # Tests that badge was earned almost 'now'
        self.assertAlmostEqual(user_badge.dateTimeObtained, now(), delta = timedelta(seconds = 1))


    def test_user_default_badge_updates_when_new_badge_won(self):
        '''Tests that the default badge ID changes when the user earns a new badge'''

        # Logs enough visits for both 1st and 2nd badges to be owned
        log_visit(self.request.wsgi_request)
        log_visit(self.request.wsgi_request)

        badge_2 = Badge.objects.get(badgeId = self.badge_2.badgeId)
        this_user = User.objects.get(userId = self.user.userId)

        self.assertEqual(this_user.defaultBadgeId.badgeId, badge_2.badgeId, 'The User\'s default badge should reference the earned badge with the highest coffee requirement')

    def test_coffee_created_if_does_not_exist(self):
        '''Tests that a new coffee object is created for the passed name if none exists'''

        # Simulates a new query with non-existent coffee name
        self.client.post(reverse('log_visit'), {'userId': self.user.userId, 'shopId': self.shop.shopId, 'coffeeName': 'latte'})

        self.assertEqual(Coffee.objects.get(id = 2).name, 'latte', 'A new coffee should be created with name latte')
        
        #ideas:

        # test removability of data if implemented
        # tests handling of large numbers of users
        # handling of user deletion
        # ensure no 2 users share usershop or userbadge as a result of the deletion
        # coffee tests / shop tests (1 user)