from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from EcoffeeBase.models import CustomUser, Badge, Shop, UserShop
from EcoffeeBase.forms import ProfileImageForm
from django.utils.timezone import now, timedelta


class TestChallengesDisplay(TestCase):
    """Tests for the display of challenges and progress in the Ecoffee app"""

    def setUp(self):
        """Set up test data - users, badges, and shops"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create badges with different levels
        self.badge1 = Badge.objects.create(
            coffee_until_earned=5, badge_image='badge_lv1.png')
        self.badge2 = Badge.objects.create(
            coffee_until_earned=10, badge_image='badge_lv2.png')
        self.badge3 = Badge.objects.create(
            coffee_until_earned=20, badge_image='badge_lv3.png')

        # Create a shop
        self.shop = Shop.objects.create(
            shop_name='Test Coffee Shop',
            number_of_visits=100,
            active_code='TESTCODE123'
        )

        # Create custom user with basic progress
        self.custom_user = CustomUser.objects.get(user=self.user)
        self.custom_user.cups_saved = 7
        self.custom_user.default_badge_id = self.badge1
        self.custom_user.most_recent_shop_id = self.shop
        self.custom_user.last_active_date_time = now()
        self.custom_user.save()

        # Set up the test client
        self.client = Client()

    def test_dashboard_badge_display(self):
        """Test that the dashboard correctly displays the user's current badge"""
        # Log in
        self.client.login(username='testuser', password='testpass123')

        # Access dashboard
        response = self.client.get(reverse('dashboard'))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the correct badge file is passed to the template
        self.assertEqual(response.context['badge_file'], 'badge_lv1.png')

    def test_progress_calculation(self):
        """Test that progress towards the next badge is correctly calculated"""
        # Log in
        self.client.login(username='testuser', password='testpass123')

        # Access dashboard
        response = self.client.get(reverse('dashboard'))

        # Check that progress is calculated correctly
        # User has 7 cups, next badge requires 10, so they need 3 more cups
        self.assertEqual(response.context['coffees_to_next_badge'], 3)

        # Progress should be correct percentage
        expected_progress = 70  # 7/10 = 70%
        self.assertEqual(response.context['progress'], expected_progress)

    def test_completed_all_challenges(self):
        """Test display when user has completed all available badges/challenges"""
        # Update user to have earned all badges
        self.custom_user.cups_saved = 25
        self.custom_user.default_badge_id = self.badge3
        self.custom_user.save()

        # Log in
        self.client.login(username='testuser', password='testpass123')

        # Access dashboard
        response = self.client.get(reverse('dashboard'))

        # Since they have the highest badge, they should get the "completed all" value
        self.assertEqual(response.context['coffees_to_next_badge'], 1000000000)
        self.assertEqual(response.context['progress'], 100)

    def test_homepage_daily_goal_progress(self):
        """Test that the homepage shows daily goal progress"""
        # Log in
        self.client.login(username='testuser', password='testpass123')

        # Access homepage
        response = self.client.get(reverse('home'))

        # Check that daily progress values are in the context
        self.assertIn('progress_percentage', response.context)
        self.assertIn('cups_saved_today', response.context)

        # Progress percentage should be calculated based on daily goal (100)
        self.assertGreaterEqual(response.context['progress_percentage'], 0)
        self.assertLessEqual(response.context['progress_percentage'], 100)

    def test_leaderboards_display(self):
        """Test that leaderboards are displayed on the homepage"""
        # Create some additional users with different cup counts
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        custom_user2 = CustomUser.objects.get(user=user2)
        custom_user2.cups_saved = 15
        custom_user2.save()

        user3 = User.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='testpass123'
        )
        custom_user3 = CustomUser.objects.get(user=user3)
        custom_user3.cups_saved = 3
        custom_user3.save()

        # Log in
        self.client.login(username='testuser', password='testpass123')

        # Access homepage
        response = self.client.get(reverse('home'))

        # Check that leaderboards are included in context
        self.assertIn('top_10_users', response.context)
        self.assertIn('top_5_shops', response.context)

        # Verify the order of users in the leaderboard
        top_users = response.context['top_10_users']
        self.assertEqual(top_users[0], custom_user2)
        self.assertEqual(top_users[1], self.custom_user)
        self.assertEqual(top_users[2], custom_user3)


class TestViews(TestCase):

    def setUp(self):
        '''Sets up a DB with test objects'''

        # Creates sufficient objects to populate leaderboards
        self.shops = {}
        self.users = {}
        self.custom_users = {}
        self.badge = Badge.objects.create(
            coffee_until_earned=4, badge_image='Badage Lv1 2.png')

        for i in range(1, 6):
            self.shops[i] = Shop.objects.create(shop_name=f'Shop_{i}', active_code=f'{i}{i+1}{i+2}',
                                                number_of_visits=i*3)

        for i in range(1, 11):
            self.users[i] = User.objects.create_user(
                username=f'user_{i}', password=f'password_{i}', first_name=f'FName_{i}',
                last_name=f'LName_{i}')
            if not CustomUser.objects.filter(user=self.users[i]).exists():
                self.custom_users[i] = CustomUser.objects.create(
                    user=self.users[i], cups_saved=0)
            else:
                self.custom_users[i] = CustomUser.objects.get(
                    user=self.users[i])
            # Stores user badges
            self.custom_users[i].default_badge_id = self.badge
            self.custom_users[i].save()

    def test_settings_displays_correctly(self):
        """Tests that settings displays correctly"""
        self.client.login(username='user_1', password='password_1')
        response = self.client.get(reverse('settings'))

        self.assertEqual(response.status_code, 200,
                         'Settings access should be accepted')
        self.assertTemplateUsed(response, 'settings.html',
                                'User should be redirected to settings')

        # Checks form
        self.assertIn('picture_form', response.context,
                      'Settings should display a form')
        self.assertIsInstance(response.context['picture_form'], ProfileImageForm, 'Form should be of the'
                              'correct type')

    def test_dashboard_accessible_if_authenticated(self):
        """Tests that dashboard is only accessible when logged in"""

        # Attempts dashboard access when logged in and out
        response_unauthenticated = self.client.get(reverse('dashboard'))

        self.assertRedirects(response_unauthenticated, reverse('login'), status_code=302,
                             target_status_code=200, msg_prefix='If logged out, dashboard access '
                             'attempts should be redirected')

        self.client.login(username=f'user_1', password='password_1')
        response_authenticated = self.client.get(reverse('dashboard'))

        self.assertEqual(response_authenticated.status_code, 200,
                         'Dashboard access should be accepted if logged in')

        self.assertTemplateUsed(response_authenticated, 'dashboard.html',
                                'User should be redirected to the dashboard')

    def test_dashboard_displays_correct_data(self):
        """Tests the dashboard displays correct statistics"""

        self.shops[1].refresh_from_db()
        this_shop = self.shops[1]

        # Logs 5 visits
        for i in range(1, 6):
            self.client.post(reverse('log_visit'), {
                'username': 'user_1',
                'shop_id': this_shop.shop_id
            })

        self.client.login(username='user_1', password='password_1')
        response = self.client.get(reverse('dashboard'))

        self.assertIn('coffees_saved', response.context, 'Dashboard should display '
                      'coffees_saved')

        self.assertIn('money_saved', response.context,
                      'Dashboard should display money_saved')

        self.assertIn('most_popular_shop', response.context, 'Dashboard should display '
                      'most_popular_shop')

        self.assertIn('badge_file', response.context, 'Dashboard should display user\'s '
                      'badge')

        self.assertEqual(response.context['coffees_saved'], 5,
                         'Dashboard should display the correct coffees_saved')

        self.assertEqual(response.context['money_saved'], '1.0',
                         'Dashboard should display the correct money_saved, currently '
                         '0.2 * 5')

        self.assertEqual(response.context['most_popular_shop'],
                         Shop.objects.order_by('-number_of_visits').first(),
                         'Dashboard should display the correct most visited shop')

    def test_home_displays_correct_data(self):
        """Tests the home page displays correct stats"""

        # Tests user stats logged out and access to home
        response_unauthenticated = self.client.get(reverse('home'))

        self.assertEqual(response_unauthenticated.status_code, 200,
                         'Homepage access request should be accepted')

        self.assertTemplateUsed(response_unauthenticated, 'homepage.html',
                                'User should be redirected to the homepage')

        self.assertIn('personal_cups_saved', response_unauthenticated.context,
                      'Homepage should display personal_cups_saved')

        # Logs in to test other stats
        self.client.login(username='user_1', password='password_1')
        response_authenticated = self.client.get(reverse('home'))

        self.assertEqual(response_authenticated.context['personal_cups_saved'], 0,
                         'Initial personal saved cups should be 0')

        self.assertIn('cups_saved_today', response_authenticated.context,
                      'Homepage should display cups_saved_today')

        self.assertIn('progress_percentage', response_authenticated.context,
                      'Homepage should display progress_percentage')

        self.assertIn('total_cups_saved', response_authenticated.context,
                      'Homepage should display total_cups_saved')

    def test_home_displays_correct_leaderboard_data(self):
        """Tests the home page displays correct leaderboard stats"""

        response = self.client.get(reverse('home'))

        self.assertIn('top_5_shops', response.context,
                      'Homepage should display top_5_shops')

        self.assertIn('top_10_users', response.context,
                      'Homepage should display top_10_users')

        user_leaderboard = response.context['top_10_users']
        shop_leaderboard = response.context['top_5_shops']

        self.assertEqual(len(user_leaderboard), 10,
                         'Users leaderboard should have size 10')

        for i in range(len(user_leaderboard) - 1):
            self.assertGreaterEqual(user_leaderboard[i].cups_saved,
                                    user_leaderboard[i+1].cups_saved,
                                    'User leaderboard should correctly rank by saved cups')

        self.assertEqual(len(shop_leaderboard), 5,
                         'Shop leaderboard should have size 5')

        for i in range(len(shop_leaderboard) - 1):
            self.assertGreaterEqual(shop_leaderboard[i].number_of_visits,
                                    shop_leaderboard[i+1].number_of_visits,
                                    'Shop leaderboard should correctly rank by saved cups')


class TestSystemIntegration(TestCase):

    def setUp(self):

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

        # Creates badges
        self.badge_1 = Badge.objects.create(coffee_until_earned=1)
        self.badge_2 = Badge.objects.create(coffee_until_earned=3)

        self.client.post(reverse('log_visit'), {  # Logs initial visit to shop 2 by user 2
            'username': '2',
            'shop_id': self.shop_2.shop_id
        })

    def test_user_lifecycle(self):
        """Tests the complete user experience, including registration, shop visiting 
        and leaderboards"""

        self.shop_1.refresh_from_db()
        self.shop_2.refresh_from_db()
        self.custom_user_1.refresh_from_db()
        this_user = self.custom_user_1
        shop_1 = self.shop_1
        shop_2 = self.shop_2

        # Logs in user 1
        self.client.login(username='1', password='password_1')

        # Tests Initial dashboard and home stats
        response_dashboard_0 = self.client.get(reverse('dashboard'))
        response_home_0 = self.client.get(reverse('home'))

        self.assertEqual(response_dashboard_0.context['coffees_saved'], 0, 'Initial '
                         'saved coffees should be 0')

        self.assertEqual(response_dashboard_0.context['badge_file'], 'defaultbadge.png',
                         'Initial badge should be default')

        self.assertEqual(response_dashboard_0.context['money_saved'], '0.0', 'Initial '
                         'progress should be 0')

        self.assertEqual(response_home_0.context['personal_cups_saved'], 0, 'Initial '
                         'personal saved cups should be 0')

        self.assertEqual(response_home_0.context['total_cups_saved'], 1, 'total '
                         'cups saved should be 1')

        self.assertEqual((response_home_0.context['top_10_users'][0].cups_saved,
                          response_home_0.context['top_10_users'][1].cups_saved), (1, 0),
                         'Leaderboard should show correct rankings and cups')

        # Visits shop 1
        self.client.post(reverse('log_visit'), {
            'username': '1',
            'shop_id': shop_1.shop_id
        })

        this_user.refresh_from_db()

        # Tests new stats
        response_dashboard_1 = self.client.get(reverse('dashboard'))
        response_home_1 = self.client.get(reverse('home'))

        self.assertEqual(response_dashboard_1.context['coffees_saved'], 1, 'Dashboard should '
                         'update coffees saved after visit')

        self.assertEqual(response_dashboard_1.context['badge_file'], 'defaultbadge.png',
                         'Dashboard should update user\'s badge')

        self.assertEqual(response_dashboard_1.context['money_saved'], '0.2', 'Progress should '
                         'update to 1 after visit')

        self.assertEqual(response_home_1.context['personal_cups_saved'], 1, 'Personal '
                         'cups saved should be updated after visit')

        self.assertEqual(response_home_1.context['total_cups_saved'], 2, 'total '
                         'cups saved should be 2 after visit')

        self.assertEqual((response_home_1.context['top_10_users'][0].cups_saved,
                          response_home_1.context['top_10_users'][1].cups_saved), (1, 1),
                         'Leaderboard should show correct rankings and cups')

        # Visits shop 2 multiple times
        self.client.post(reverse('log_visit'), {
            'username': '1',
            'shop_id': shop_2.shop_id
        })
        self.client.post(reverse('log_visit'), {
            'username': '1',
            'shop_id': shop_2.shop_id
        })

        this_user.refresh_from_db()

        response_dashboard_2 = self.client.get(reverse('dashboard'))
        response_home_2 = self.client.get(reverse('home'))

        self.assertEqual(response_dashboard_2.context['coffees_saved'], 3, 'Dashboard should '
                         'update coffees saved after multiple visits')

        self.assertEqual(response_dashboard_2.context['badge_file'], 'defaultbadge.png',
                         'Dashboard should update user\'s badge')

        self.assertEqual(response_dashboard_2.context['money_saved'], '0.6', 'Progress should '
                         'update after multiple visits')

        self.assertEqual(response_home_2.context['personal_cups_saved'], 3, 'Personal '
                         'cups saved should be updated after multiple visits')

        self.assertEqual(response_home_2.context['total_cups_saved'], 4, 'total '
                         'cups saved should be 4 after multiple visits')

        self.assertEqual((response_home_2.context['top_10_users'][0].cups_saved,
                          response_home_2.context['top_10_users'][1].cups_saved), (3, 1),
                         'Leaderboard should show correct rankings and cups')

    def test_shop_life_cycle(self):
        """Tests a complete shop lifecycle for multiple customers and days"""

        self.shop_1.refresh_from_db()
        self.shop_2.refresh_from_db()
        self.custom_user_2.refresh_from_db()
        shop_1 = self.shop_1
        shop_2 = self.shop_2
        user_2 = self.custom_user_2
        try:
            this_user_shop = UserShop.objects.get(
                user=self.custom_user_2, shop_id=self.shop_2)
        except UserShop.DoesNotExist:
            print("UserShop instance should be created for the user - shop pair")

        # Logs in user 2
        self.client.login(username='2', password='password_2')

        # Tests Initial dashboard and home stats
        response_dashboard_0 = self.client.get(reverse('dashboard'))
        response_home_0 = self.client.get(reverse('home'))

        self.assertEqual(response_dashboard_0.context['most_popular_shop'], shop_2,
                         'Initial most popular shop should be 2')

        self.assertEqual(response_dashboard_0.context['most_visited_shop'], this_user_shop,
                         'Initial most visited shop should be 2')

        self.assertEqual(response_dashboard_0.context['percentage_above_average'], 100,
                         'Percentage saved above average should be 100')

        self.assertEqual(response_home_0.context['cups_saved_today'], 0, 'Initial '
                         'cups saved today should be 0')

        self.assertEqual(response_home_0.context['progress_percentage'], 0, 'Initial '
                         'progress percentage should be 0')

        self.assertEqual((response_home_0.context['top_5_shops'][0].number_of_visits,
                          response_home_0.context['top_5_shops'][1].number_of_visits), (1, 0),
                         'Leaderboard should show correct rankings and visits')

        # User 1 visits 1st shop multiple times
        self.client.post(reverse('log_visit'), {
            'username': '1',
            'shop_id': shop_1.shop_id
        })
        self.client.post(reverse('log_visit'), {
            'username': '1',
            'shop_id': shop_1.shop_id
        })

        shop_1.refresh_from_db()
        user_2.refresh_from_db()

        # Tests new stats
        response_dashboard_1 = self.client.get(reverse('dashboard'))
        response_home_1 = self.client.get(reverse('home'))

        self.assertEqual(response_dashboard_1.context['most_popular_shop'], shop_1, 'most '
                         'popular shop should update after other users\' visit')

        self.assertEqual(response_dashboard_1.context['most_visited_shop'], this_user_shop,
                         'most visited shop should remain 2 after other users\' visits')

        self.assertEqual(response_dashboard_1.context['percentage_above_average'], 33.33333333333333,
                         'Percentage saved above average should update after other users\' visits')

        self.assertEqual(response_home_1.context['cups_saved_today'], 0, 'Cups saved today '
                         'should update after other users\' visits')

        self.assertEqual(response_home_1.context['progress_percentage'], 0, 'Progress percentage '
                         'should update after other users\' visits')

        self.assertEqual((response_home_1.context['top_5_shops'][0].number_of_visits,
                          response_home_1.context['top_5_shops'][1].number_of_visits), (2, 1),
                         'Leaderboard should show correct rankings and visits')

        self.assertEqual((response_home_1.context['top_10_users'][0].cups_saved,
                          response_home_1.context['top_10_users'][1].cups_saved), (2, 1),
                         'Leaderboard should show correct rankings and cups')

        # User 2 visits shop 1 multiple times over 2 days
        self.client.post(reverse('log_visit'), {
            'username': '2',
            'shop_id': shop_1.shop_id
        })

        self.user_2.last_active_date_time = now() - timedelta(days=1)
        self.user_2.save()

        self.client.post(reverse('log_visit'), {
            'username': '2',
            'shop_id': shop_1.shop_id
        })

        # Tests new stats
        response_dashboard_2 = self.client.get(reverse('dashboard'))
        response_home_2 = self.client.get(reverse('home'))

        shop_2.refresh_from_db()
        user_2.refresh_from_db()

        self.assertEqual(response_dashboard_2.context['most_popular_shop'], shop_1, 'most '
                         'popular shop should remain 1 after user visits')

        self.assertNotEqual(response_dashboard_2.context['most_visited_shop'], this_user_shop,
                            'most visited shop should update after other users\' visits')

        self.assertEqual(response_dashboard_2.context['percentage_above_average'], 33.33333333333333,
                         'Percentage saved above average should update after user visits')

        self.assertEqual(response_home_2.context['cups_saved_today'], 0, 'Cups saved today '
                         'should update after user visits and days')

        self.assertEqual(response_home_2.context['progress_percentage'], 0.0, 'Progress percentage '
                         'should update after user visits and days')

        self.assertEqual((response_home_2.context['top_5_shops'][0].number_of_visits,
                          response_home_2.context['top_5_shops'][1].number_of_visits), (4, 1),
                         'Leaderboard should show correct rankings and visits')

        self.assertEqual((response_home_2.context['top_10_users'][0].cups_saved,
                          response_home_2.context['top_10_users'][1].cups_saved), (2, 1),
                         'Leaderboard should show correct rankings and cups')
