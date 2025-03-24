from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from django.utils.timezone import now
from EcoffeeBase.models import Shop, CustomUser, UserShop, Badge, UserBadge
from EcoffeeBase.forms import ProfileImageForm
from EcoffeeBase.views import log_visit


class TestDataBase(TestCase):

    def setUp(self):
        '''Sets up a DB with test objects and a simulated POST request'''

        self.shop = Shop.objects.create(
            shop_name='New Shop', active_code='123', number_of_visits=0)
        self.user = User.objects.create_user(
            username='1', password='password_1', first_name='John', last_name='Smith')
        if not CustomUser.objects.filter(user=self.user).exists():
            self.custom_user = CustomUser.objects.create(
                user=self.user, cups_saved=0)
        else:
            self.custom_user = CustomUser.objects.get(user=self.user)

        # Initialises badges: different thresholds enable user.defaultBadgeId testing
        self.badge_1 = Badge.objects.create(coffee_until_earned=2)
        self.badge_2 = Badge.objects.create(coffee_until_earned=3)

        # Simulates recieving a POST request
        self.request = self.client.post(reverse('log_visit'), {
                                        'username': self.custom_user.user.username, 
                                        'shop_id': self.shop.shop_id})

    def test_shop_registers_visit(self):
        '''Tests log_visit updates Shop attributes to reflect user's visit'''

        self.shop.refresh_from_db()
        this_shop = self.shop

        self.assertEqual(this_shop.number_of_visits, 1,
                         'Shop vist count should increment on visit')

    def test_user_registers_visit(self):
        '''Tests log_visit updates User attributes to reflect a shop visit'''

        self.custom_user.refresh_from_db()
        this_user = self.custom_user

        self.assertEqual(this_user.most_recent_shop_id, self.shop,
                         'The visited shop should be set as the user\'s most recent shop')

        self.assertEqual(this_user.cups_saved, 1,
                         'User\'s cups saved count should increment on visit')

        self.assertAlmostEqual(
            this_user.last_active_date_time, now(), delta=timedelta(seconds=1))

    def test_user_shop_registers_visit(self):
        '''Tests log_visit updates UserShop attributes to reflect a user's visit'''

        try:
            this_user_shop = UserShop.objects.get(
                user=self.custom_user, shop_id=self.shop)
        except UserShop.DoesNotExist:
            print("UserShop instance should be created for the user - shop pair")

        self.assertEqual(this_user_shop.user, self.custom_user,
                         'The UserShop instance should reference the correct parent User')

        self.assertEqual(this_user_shop.shop_id, self.shop,
                         'The UserShop instance should reference the correct parent Shop')

        self.assertEqual(this_user_shop.visit_amounts, 1,
                         'UserShop vist count should increment on visit')

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
            user_badge = UserBadge.objects.get(
                badge_id=this_badge, user=this_user)
        except UserBadge.DoesNotExist:
            print("UserBadge instance should be created for the user - badge pair")

        # Tests user fields updated
        self.assertEqual(this_user.default_badge_id, this_badge,
                         'Initial earned badge should be set as the User\'s default badge')

        # Tests that badge was earned almost 'now'
        self.assertAlmostEqual(user_badge.date_time_obtained,
                               now(), delta=timedelta(seconds=1))

    def test_user_default_badge_updates_when_new_badge_won(self):
        '''Tests that the default badge ID changes when the user earns a new badge'''

        # Logs enough visits for both 1st and 2nd badges to be owned
        log_visit(self.request.wsgi_request)
        log_visit(self.request.wsgi_request)

        self.badge_2.refresh_from_db()
        self.custom_user.refresh_from_db()
        badge_2 = self.badge_2
        this_user = self.custom_user

        self.assertEqual(this_user.default_badge_id, badge_2,
                         'The User\'s default badge should reference the earned badge with the '
                         'highest coffee requirement')
    
    def test_response_returns_error_if_nonexistent_user(self):
        """Tests attempting to log a visit for a non-existent user raises 404"""

        self.shop.refresh_from_db()
        this_shop = self.shop

        response = self.client.post(reverse('log_visit'), {
            'username': 'wrong_name', 
            'shop_id': this_shop
        })
        self.assertEqual(response.status_code, 404)

    def test_response_returns_error_if_nonexistent_shop(self):
        """Tests attempting to log a visit for a non-existent shop raises 404"""

        self.custom_user.refresh_from_db()
        this_username = self.custom_user.user.username

        response = self.client.post(reverse('log_visit'), {
            'username': this_username, 
            'shop_id': 3
        })
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_revisit_shop_same_day(self):

        self.shop.refresh_from_db()
        this_shop = self.shop
        try:
            this_user_shop = UserShop.objects.get(
                user=self.custom_user, shop_id=self.shop)
        except UserShop.DoesNotExist:
            print("UserShop instance should be created for the user - shop pair")

        # Simulates 2 visits
        this_user_shop.visit_amounts += 1
        this_user_shop.save()
        this_user_shop.visit_amounts += 1
        this_user_shop.save()

        this_user_shop.refresh_from_db()
        this_shop.refresh_from_db()

        self.assertEqual(this_user_shop.visit_amounts, 1, "User shop should not log multiple visits "
        "in a day")

        self.assertEqual(this_shop.number_of_visits, 1, "Shop's visit total should not reflect multiple "
        "daily same-user visits")

class TestDataBaseMultipleObjects(TestCase):

    def setUp(self):
        '''Sets up a DB with test objects'''

        # Multiple shops and users
        self.shop_1 = Shop.objects.create(
            shop_name='New Shop 1', active_code='123', number_of_visits=0)
        self.shop_2 = Shop.objects.create(
            shop_name='New Shop 2', active_code='456', number_of_visits=0)
        self.user_1 = User.objects.create_user(
            username='1', password='password_1', first_name='John', last_name='One')
        self.user_2 = User.objects.create_user(
            username='2', password='password_2', first_name='Jane', last_name='Two')
        if (not CustomUser.objects.filter(user=self.user_1).exists()
            ) or (not CustomUser.objects.filter(user=self.user_2).exists()):
            self.custom_user_1 = CustomUser.objects.create(
                user=self.user_1, cups_saved=0)
            self.custom_user_2 = CustomUser.objects.create(
                user=self.user_2, cups_saved=0)
        else:
            self.custom_user_1 = CustomUser.objects.get(user=self.user_1)
            self.custom_user_2 = CustomUser.objects.get(user=self.user_2)

    def test_multiple_users_can_visit_shop(self):
        """Tests that multiple user visits to the same shop are logged"""

        this_shop = self.shop_1
        this_user_1 = self.custom_user_1
        this_user_2 = self.custom_user_2
        
        # Logs visits
        self.client.post(reverse('log_visit'), {
            'username': this_user_1.user.username, 
            'shop_id': this_shop.shop_id
        })
        self.client.post(reverse('log_visit'), {
            'username': this_user_2.user.username, 
            'shop_id': this_shop.shop_id
        })

        this_shop.refresh_from_db()
        this_user_1.refresh_from_db()
        this_user_2.refresh_from_db()
        user_1_shop = UserShop.objects.get(user=this_user_1, shop_id=this_shop)
        user_2_shop = UserShop.objects.get(user=this_user_2, shop_id=this_shop)
        
        self.assertEqual(this_shop.number_of_visits, 2, 
                         'Shop vist count should increment for visits by different users')
        
        self.assertEqual((this_user_1.cups_saved, this_user_2.cups_saved), (1, 1), 
                         'Cups saved should update for all users of one shop')

        self.assertEqual((user_1_shop.visit_amounts, user_2_shop.visit_amounts), (1, 1),
                         'User Shop visits should update for all users of one shop')

    def test_user_can_visit_multiple_shops(self):
        """Tests that multiple shops log visits by the same user"""
        
        this_shop_1 = self.shop_1
        this_shop_2 = self.shop_2
        this_user = self.custom_user_2

        self.client.post(reverse('log_visit'), {
            'username': this_user.user.username, 
            'shop_id': this_shop_1.shop_id
        })
        self.client.post(reverse('log_visit'), {
            'username': this_user.user.username, 
            'shop_id': this_shop_2.shop_id
        })
        
        this_shop_1.refresh_from_db()
        this_shop_2.refresh_from_db()
        this_user.refresh_from_db()
        user_shop_1 = UserShop.objects.get(user=this_user, shop_id=this_shop_2)
        user_shop_2 = UserShop.objects.get(user=this_user, shop_id=this_shop_2)
        
        self.assertEqual((this_shop_1.number_of_visits, this_shop_2.number_of_visits), (1, 1), 
                         'All shops visited by a single user should log the user\'s visit')
        
        self.assertEqual(this_user.cups_saved, 2, 
                         'Cups saved should update to reflect visits to multiple shops')
        
        self.assertEqual(this_user.most_recent_shop_id, this_shop_2.shop_id, 
                         'Most recent shop ID should reflect users\' most recently visited shop')
        
        self.assertEqual((user_shop_1.visit_amounts, user_shop_2.visit_amounts),(1, 1), 
                         'Visiting multiple shops should increase each User Shop\'s visit count '
                         'for that user')