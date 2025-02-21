from django.test import TestCase
from django.urls import reverse
from models import Shop, User, UserShop, Badge, UserBadge, Coffee
from views import log_visit

class DataBaseTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        '''Sets up a DB with test objects'''
        cls.obj = Shop.objects.create(firstName = 'John', lastName = 'Smith')
        cls.obj = User.objects.create(shopName = 'New Shop', activeCode = '123')
        cls.obj = Badge.objects.create()
        cls.obj = Coffee.objects.create(name = 'espresso')

    def setUp(self):
        '''Sets up a simulated POST request'''
        self.request = self.client.post(reverse(), {'userId' : 1, 'shopId' : 1, 'coffeeName' : 'espresso'}) # sort out reverse

    def testShopRegistersVisit(self, cls):
        '''Tests log_visit updates Shop attributes to reflect user's visit'''

        # Simulates recieving the POST request
        log_visit(self.request)

        this_shop = cls.objShop.objects.get(shopId = 1)

        TestCase.assertEqual(this_shop.numberOfVisits, 1)

    def testUserRegistersVisit(self, cls):
        '''Tests log_visit updates User attributes to reflect a shop visit'''

        log_visit(self.request)

        this_user = cls.objShop.objects.get(userId = 1)

        TestCase.assertEqual(this_user.mostRecentShopId, 1)

        TestCase.assertEqual(this_user.progression, 1)

        TestCase.assertEqual(this_user.cupsSaved, 1)

        #todo: check that time of visit = almost now


# Tests for EcoffeeBase
