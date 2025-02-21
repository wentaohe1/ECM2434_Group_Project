from django.test import TestCase
from django.urls import reverse
from models import Shop, User, UserShop, Badge, UserBadge, Coffee
from views import log_visit

class DataBaseTests(TestCase):
    @classmethod
    def set_up_test_data(cls):
        '''Sets up a DB with test objects'''
        cls.obj = Shop.objects.create(firstName = 'John', lastName = 'Smith')
        cls.obj = User.objects.create(shopName = 'New Shop', activeCode = '123')
        cls.obj = Coffee.objects.create(name = 'espresso')

        # Initialises badges: different thresholds enable user.defaultBadgeId testing
        cls.obj = Badge.objects.create(coffeeUntilEarned = 1)
        cls.obj = Badge.objects.create(coffeeUntilEarned = 2)

    def set_up(self):
        '''Sets up a simulated POST request'''
        self.request = self.client.post(reverse(), {'userId' : 1, 'shopId' : 1, 'coffeeName' : 'espresso'}) # sort out reverse

    def test_shop_registers_visit(self, cls):
        '''Tests log_visit updates Shop attributes to reflect user's visit'''

        # Simulates recieving the POST request
        log_visit(self.request)

        this_shop = cls.objShop.objects.get(shopId = 1)

        TestCase.assertEqual(this_shop.numberOfVisits, 1)

    def test_user_registers_visit(self, cls):
        '''Tests log_visit updates User attributes to reflect a shop visit'''

        log_visit(self.request)

        this_user = cls.objShop.objects.get(userId = 1)

        TestCase.assertEqual(this_user.mostRecentShopId, 1)

        TestCase.assertEqual(this_user.progression, 1)

        TestCase.assertEqual(this_user.cupsSaved, 1)

        #todo: check that time of visit = almost now

    def test_user_shop_registers_visit(self, cls):
        '''Tests log_visit updates UserShop attributes to reflect a user's visit'''

        log_visit(self.request)

        this_userShop = cls.objShop.objects.get(userId = 1, shopId = 1)

        TestCase.assertEqual(this_userShop.userId, 1)

        TestCase.assertEqual(this_userShop.shopId, 1)

        TestCase.assertEqual(this_userShop.visitAmounts, 1)

    def test_user_shop_registers_visit(self, cls):
        '''Tests log_visit updates UserShop attributes to reflect a user's visit'''

        log_visit(self.request)

        this_badge = cls.objShop.objects.get(badgeId = 1) # 1st badge
        this_user = cls.objShop.objects.get(userId = 1)
        UserBadge = cls.objShop.objects.get(badgeId = 1, userId = 1)

        # Tests user fields updated
        TestCase.assertEqual(this_user.progression, 0)

        TestCase.assertEqual(this_user.defaultBadgeId, this_badge.badgeId)

        # Tests user_badge fields updated
        TestCase.assertEqual(this_user.owned, True)

        #test that badge was earned 'now'

    def test_user_default_badge_updates_when_new_badge_won(self, cls):
        '''Tests that the default badge ID changes when the user earns a new badge'''

        # Logs enough visits for both 1st and 2nd badges to be owned
        log_visit(self.request)
        log_visit(self.request)

        badge_2 = cls.objShop.objects.get(badgeId = 2) # 2nd badge
        this_user = cls.objShop.objects.get(userId = 1)

        TestCase.assertEqual(this_user.defaultBadgeId, badge_2.badgeId)





    



# Tests for EcoffeeBase
