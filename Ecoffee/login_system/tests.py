from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.db import transaction
from EcoffeeBase.models import CustomUser, Badge, Shop
import unittest


class LoginSystemTests(TestCase):
    """Test suite for authentication system functionality"""

    @classmethod
    def setUpTestData(cls):
        """
        Set up data used for all test methods.
        This is more efficient than setUp as it's only called once for the class.
        """
        cls.User = get_user_model()
        # Create test user but don't test the creation in this method
        cls.test_user = cls.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        cls.test_custom_user = CustomUser.objects.get(user=cls.test_user)
        cls.test_custom_user.is_email_verified = True
        cls.test_custom_user.save()

    def setUp(self):
        """Set up before each test method"""
        # Create a fresh client for each test
        self.client = Client()

    def test_user_creation(self):
        """Test user creation with proper attributes"""
        self.assertEqual(self.test_user.username, 'testuser')
        self.assertEqual(self.test_user.email, 'test@example.com')
        self.assertTrue(self.test_user.check_password('testpass123'))

        # Verify customuser object was created via signal
        self.assertTrue(CustomUser.objects.filter(
            user=self.test_user).exists())

    def test_login_view_get(self):
        """Test login view GET request returns correct page"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authenticate/login.html')

    def test_login_success(self):
        """Test successful login with valid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Check redirect to home page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get('Location'), '/home/')

        # Verify user is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_failure_wrong_password(self):
        """Test login failure with incorrect password"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authenticate/login.html')

        # Should have error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Invalid username or password" in str(msg)
                        for msg in messages))

        # User should not be authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_failure_nonexistent_user(self):
        """Test login failure with non-existent username"""
        response = self.client.post(reverse('login'), {
            'username': 'nonexistentuser',
            'password': 'testpass123'
        })
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authenticate/login.html')

        # Should have error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Invalid username or password" in str(msg)
                        for msg in messages))

    def test_login_redirects_authenticated_user(self):
        """Test that an already authenticated user is redirected from login page"""
        # First log in
        self.client.login(username='testuser', password='testpass123')

        # Then try to access login page
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get('Location'), '/home/')

    def test_logout(self):
        """Test logout functionality"""
        # First log in
        self.client.login(username='testuser', password='testpass123')

        # Then logout
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get(
            'Location'), '/login_system/login_user')

        # Verify user is no longer authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_register_view_get(self):
        """Test GET request to register page"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authenticate/register_user.html')
        # Check if form is included in context
        self.assertIn('form', response.context)

    def test_register_success(self):
        """Test successful registration with valid data"""
        initial_user_count = self.User.objects.count()

        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'securepwd123',
            'password2': 'securepwd123',
            'email': 'newuser@example.com'
        })

        # Check redirect
        self.assertEqual(response.status_code, 302)

        # Check user was created
        self.assertEqual(self.User.objects.count(), initial_user_count + 1)

        # Verify the user data
        new_user = self.User.objects.get(username='newuser')
        self.assertTrue(new_user.check_password('securepwd123'))
        self.assertEqual(new_user.email, 'newuser@example.com')

        # Verify CustomUser was created via signal
        self.assertTrue(CustomUser.objects.filter(user=new_user).exists())

    def test_register_failure_password_mismatch(self):
        """Test registration failure when passwords don't match"""
        initial_user_count = self.User.objects.count()

        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'securepwd123',
            'password2': 'differentpwd123',
            'email': 'newuser@example.com'
        })

        # Should stay on register page
        self.assertEqual(response.status_code, 200)

        # No new user should be created
        self.assertEqual(self.User.objects.count(), initial_user_count)

        # Should have form errors
        self.assertTrue(response.context['form'].errors)

    def test_register_failure_existing_username(self):
        """Test registration failure when username already exists"""
        initial_user_count = self.User.objects.count()

        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password1': 'securepwd123',
            'password2': 'securepwd123',
            'email': 'different@example.com'
        })

        # Should stay on register page
        self.assertEqual(response.status_code, 200)

        # No new user should be created
        self.assertEqual(self.User.objects.count(), initial_user_count)

        # Should have form errors
        self.assertTrue(response.context['form'].errors)

    def test_login_user_email_not_activated(self):
        self.test_custom_user.is_email_verified = False
        self.test_custom_user.save()
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authenticate/login.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Please verify your email" in str(message)
                        for message in messages))

    def test_login_user_email_activated(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get('Location'), '/home/')


class GDPRComplianceTests(TestCase):
    """Test suite for GDPR compliance functionality"""

    @classmethod
    def setUpTestData(cls):
        """Set up data used for all test methods"""
        # Create models used across tests
        cls.User = get_user_model()
        cls.test_user = cls.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create some badges for testing
        cls.badge = Badge.objects.create(
            coffee_until_earned=5, badge_image='badge_test.png')

        # Create a shop for testing
        cls.shop = Shop.objects.create(
            shop_name='Test Shop',
            active_code='TEST123'
        )

    def setUp(self):
        """Set up before each test method"""
        self.client = Client()
        # Log in for tests requiring authentication
        self.client.login(username='testuser', password='testpass123')

    def test_data_minimization(self):
        """Test that only necessary data is collected per GDPR requirements"""
        # Get the custom user for testing
        custom_user = CustomUser.objects.get(user=self.test_user)

        # Define necessary fields based on application requirements
        necessary_fields = [
            'id',
            'user', 'cups_saved', 'most_recent_shop_id',
            'default_badge_id', 'last_active_date_time',
            'streak', 'streak_start_day', 'is_email_verified', 'email_verification_token', 'profile_image'
        ]

        # Define expected relationship fields (excluded from validation)
        relationship_fields = ['usershop', 'userbadge']

        # Get all field names on the model
        all_fields = [f.name for f in CustomUser._meta.get_fields()]

        # Verify only necessary fields exist (excluding relationships)
        for field in all_fields:
            if field not in relationship_fields:
                self.assertIn(field, necessary_fields,
                              f"Field '{field}' may be unnecessary and violate data minimization")

        # Verify all necessary fields are present
        for field in necessary_fields:
            self.assertIn(field, all_fields,
                          f"Required field '{field}' is missing from the CustomUser model")
