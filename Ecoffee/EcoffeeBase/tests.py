from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from django.utils.timezone import now
from EcoffeeBase.models import Shop, CustomUser, UserShop, Badge, UserBadge
from EcoffeeBase.views import log_visit

class DataBaseTests(TestCase):

    def setUp(self):
        '''Sets up a DB with test objects and a simulated POST request'''

        self.shop = Shop.objects.create(shopName = 'New Shop', activeCode = '123', numberOfVisits = 0)
        self.user = User.objects.create_user(username = '1', password = 'password_1', first_name = 'John', last_name = 'Smith')
        self.custom_user = CustomUser.objects.create(user = self.user, cupsSaved = 0)

        # Initialises badges: different thresholds enable user.defaultBadgeId testing
        self.badge_1 = Badge.objects.create(coffeeUntilEarned = 2)
        self.badge_2 = Badge.objects.create(coffeeUntilEarned = 3)

        # Simulates recieving a POST request
        self.request = self.client.post(reverse('log_visit'), {'username': self.custom_user.user.username, 'shop_id': self.shop.shopId})

    def test_shop_registers_visit(self):
        '''Tests log_visit updates Shop attributes to reflect user's visit'''

        this_shop = self.shop

        self.assertEqual(this_shop.numberOfVisits, 1, 'Shop vist count should increment on visit')

    def test_user_registers_visit(self):
        '''Tests log_visit updates User attributes to reflect a shop visit'''

        this_user = self.custom_user

        self.assertEqual(this_user.mostRecentShopId, self.shop, 'The visited shop should be set as the user\'s most recent shop')

        self.assertEqual(this_user.cupsSaved, 1, 'User\'s cups saved count should increment on visit')

        self.assertAlmostEqual(this_user.lastActiveDateTime, now(), delta = timedelta(seconds = 1))

    def test_user_shop_registers_visit(self):
        '''Tests log_visit updates UserShop attributes to reflect a user's visit'''

        try:
            this_userShop = UserShop.objects.get(user = self.custom_user, shopId = self.shop)
        except UserShop.DoesNotExist:
            print("UserShop instance should be created for the user - shop pair")

        self.assertEqual(this_userShop.user, self.custom_user, 'The UserShop instance should reference the correct parent User')

        self.assertEqual(this_userShop.shopId, self.shop, 'The UserShop instance should reference the correct parent Shop')

        self.assertEqual(this_userShop.visitAmounts, 1, 'UserShop vist count should increment on visit')

    def test_user_badge_registers_visit(self):
        '''Tests log_visit updates UserBadge attributes to reflect a user's visit'''

        # Simulates a second request
        log_visit(self.request.wsgi_request)

        this_badge = self.badge_1
        this_user = self.custom_user

        try:
            user_badge = UserBadge.objects.get(badgeId = this_badge, user = this_user)
        except UserBadge.DoesNotExist:
            print("UserBadge instance should be created for the user - badge pair")

        # Tests user fields updated
        self.assertEqual(this_user.defaultBadgeId, this_badge, 'Initial earned badge should be set as the User\'s default badge')

        # Tests user_badge fields updated
        self.assertEqual(user_badge.owned, True, 'Badge ownership status should be True once earned')

        # Tests that badge was earned almost 'now'
        self.assertAlmostEqual(user_badge.dateTimeObtained, now(), delta = timedelta(seconds = 1))


    def test_user_default_badge_updates_when_new_badge_won(self):
        '''Tests that the default badge ID changes when the user earns a new badge'''

        # Logs enough visits for both 1st and 2nd badges to be owned
        log_visit(self.request.wsgi_request)
        log_visit(self.request.wsgi_request)

        badge_2 = self.badge_2
        this_user = self.custom_user

        self.assertEqual(this_user.defaultBadgeId, badge_2, 'The User\'s default badge should reference the earned badge with the highest coffee requirement')