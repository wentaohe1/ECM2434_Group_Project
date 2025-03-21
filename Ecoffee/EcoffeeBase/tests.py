from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from EcoffeeBase.models import CustomUser, Badge, Shop
from django.utils.timezone import now
import datetime

class ChallengesDisplayTests(TestCase):
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
        self.badge1 = Badge.objects.create(coffee_until_earned=5, badge_image='badge_lv1.png')
        self.badge2 = Badge.objects.create(coffee_until_earned=10, badge_image='badge_lv2.png')
        self.badge3 = Badge.objects.create(coffee_until_earned=20, badge_image='badge_lv3.png')
        
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