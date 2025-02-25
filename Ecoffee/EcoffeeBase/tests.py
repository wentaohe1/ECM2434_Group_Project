from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from django.utils.timezone import now
from EcoffeeBase.models import Shop, CustomUser, UserShop, Badge, UserBadge
from EcoffeeBase.views import log_visit

class TestLogVisit(TestCase):
    '''Tests for the log_visit() view'''

    def setUp(self):
        '''Sets up a DB with mock objects and a simulated POST request'''

        self.shop = Shop.objects.create(shop_name = 'New Shop', active_code = '123', number_of_visits = 0)
        self.user = User.objects.create_user(username = '1', password = 'password_1', first_name = 'John', last_name = 'Smith')
        if not CustomUser.objects.filter(user = self.user).exists():
            self.custom_user = CustomUser.objects.create(user = self.user, cups_saved=0)
        else:
            self.custom_user = CustomUser.objects.get(user=self.user)

        # Initialises badges: different thresholds enable user.defaultBadgeId testing
        self.badge_1 = Badge.objects.create(coffee_until_earned = 2)
        self.badge_2 = Badge.objects.create(coffee_until_earned = 3)

        # Simulates recieving a POST request
        self.request = self.client.post(reverse('log_visit'), {'username': self.custom_user.user.username, 'shop_id': self.shop.shop_id})

    def test_shop_registers_visit(self):
        '''Tests log_visit updates Shop attributes to reflect user's visit'''

        self.shop.refresh_from_db()
        this_shop = self.shop

        self.assertEqual(this_shop.number_of_visits, 1, 'Shop vist count should increment on visit')

    def test_user_registers_visit(self):
        '''Tests log_visit updates User attributes to reflect a shop visit'''

        self.custom_user.refresh_from_db()
        this_user = self.custom_user

        self.assertEqual(this_user.most_recent_shop_id, self.shop, 'The visited shop should be set as the user\'s most recent shop')

        self.assertEqual(this_user.cups_saved, 1, 'User\'s cups saved count should increment on visit')

        self.assertAlmostEqual(this_user.last_active_date_time, now(), delta = timedelta(seconds = 1))

    def test_user_shop_registers_visit(self):
        '''Tests log_visit updates UserShop attributes to reflect a user's visit'''

        try:
            this_user_shop = UserShop.objects.get(user = self.custom_user, shop_id = self.shop)
        except UserShop.DoesNotExist:
            print("UserShop instance should be created for the user - shop pair")

        self.assertEqual(this_user_shop.user, self.custom_user, 'The UserShop instance should reference the correct parent User')

        self.assertEqual(this_user_shop.shop_id, self.shop, 'The UserShop instance should reference the correct parent Shop')

        self.assertEqual(this_user_shop.visit_amounts, 1, 'UserShop vist count should increment on visit')

    def test_user_badge_registers_visit(self):
        '''Tests log_visit updates UserBadge attributes to reflect a user's visit'''

        # Simulates a second request
        log_visit(self.request.wsgi_request)

        self.badge_1.refresh_from_db()
        self.badge_2.refresh_from_db()
        self.custom_user.refresh_from_db()
        this_badge = self.badge_1
        this_user = self.custom_user

        try:
            user_badge = UserBadge.objects.get(badge_id = this_badge, user = this_user)
        except UserBadge.DoesNotExist:
            print("UserBadge instance should be created for the user - badge pair")

        # Tests user fields updated
        self.assertEqual(this_user.default_badge_id, this_badge, 'Initial earned badge should be set as the User\'s default badge')

        # Tests that badge was earned almost 'now'
        self.assertAlmostEqual(user_badge.date_time_obtained, now(), delta = timedelta(seconds = 1))


    def test_user_default_badge_updates_when_new_badge_won(self):
        '''Tests that the default badge ID changes when the user earns a new badge'''

        # Logs enough visits for both 1st and 2nd badges to be owned
        log_visit(self.request.wsgi_request)
        log_visit(self.request.wsgi_request)

        self.badge_2.refresh_from_db()
        self.custom_user.refresh_from_db()
        badge_2 = self.badge_2
        this_user = self.custom_user

        self.assertEqual(this_user.default_badge_id, badge_2, 'The User\'s default badge should reference the earned badge with the highest coffee requirement')

class TestHomeView:
    '''Tests for the home() view'''

    def setUp(self):
        '''Sets up a DB with mock objects and a simulated POST request'''

        # Initialises badges and shop
        self.badge_1 = Badge.objects.create(coffee_until_earned = 1)
        self.badge_2 = Badge.objects.create(coffee_until_earned = 3)
        self.shop = Shop.objects.create(shop_name = 'New Shop', active_code = '123', number_of_visits = 5)

        # Creates mock users and CustomUsers
        self.user_1 = User.objects.create_user(username = '1', password = 'password_1', first_name = 'John', last_name = 'Smith')
        self.user_2 = User.objects.create_user(username = '2', password = 'password_2', first_name = 'John', last_name = 'Doe')
        self.user_3 = User.objects.create_user(username = '3', password = 'password_3', first_name = 'Jane', last_name = 'Doe')

        # Creates 2 CustomUsers with badge_1
        for user in [self.user_1, self.user_2]:
            if not CustomUser.objects.filter(user = user).exists():
                CustomUser.objects.create(user = user, cups_saved = 1, most_recent_shop_id = self.shop.last_active_date_time = now().date())
            else:
                self.custom_user = CustomUser.objects.get(user = user)

        # Creates 1 CustomUser with badge_2
        if not CustomUser.objects.filter(user = self.user_3).exists():
            self.custom_user = CustomUser.objects.create(user = self.user_3, cups_saved = 3)
        else:
            self.custom_user = CustomUser.objects.get(user = self.user_3, last_active_date_time = now().date(),)

        
