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
        self.assertTrue(CustomUser.objects.filter(user=self.test_user).exists())

    def test_login_view_get(self):
        """Test login view GET request returns correct page"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authenticate/login.html')
        # Check if form is included in context
        self.assertIn('form', response.context)

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
        self.assertTrue(any("Invalid username or password" in str(msg) for msg in messages))
        
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
        self.assertTrue(any("Invalid username or password" in str(msg) for msg in messages))

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
        self.assertEqual(response.headers.get('Location'), '/login_system/login_user')
        
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
        cls.badge = Badge.objects.create(coffee_until_earned=5, badge_image='badge_test.png')
        
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

    @unittest.skip("Privacy page not implemented yet")
    def test_privacy_policy_access(self):
        """Test that privacy policy page is accessible and contains required info"""
        try:
            response = self.client.get(reverse('privacy'))
            self.assertEqual(response.status_code, 200)
            
            # Check that the page contains relevant GDPR terms
            for term in ['privacy', 'data', 'rights', 'GDPR', 'consent']:
                self.assertContains(response, term, msg_prefix=f"Privacy policy should contain '{term}'")
                
            # Check specific GDPR rights are mentioned
            for right in ['access', 'rectification', 'erasure', 'restriction', 'portability']:
                self.assertContains(response, right, msg_prefix=f"Privacy policy should mention right to '{right}'")
        except NoReverseMatch:
            self.skipTest("Privacy page URL not configured yet")

    @unittest.skip("User data page not implemented yet")
    def test_data_access(self):
        """Test that users can access their personal data"""
        try:
            response = self.client.get(reverse('user_data'))
            self.assertEqual(response.status_code, 200)
            
            # Verify response contains user data
            self.assertContains(response, self.test_user.username)
            self.assertContains(response, self.test_user.email)
            
            # Check that the page has appropriate security measures
            self.assertIn('X-Frame-Options', response.headers)
            self.assertEqual(response.headers['X-Frame-Options'], 'DENY')
        except NoReverseMatch:
            self.skipTest("User data URL not configured yet")

    @unittest.skip("Account deletion page not implemented yet")
    def test_data_deletion(self):
        """Test that users can delete their account and all data"""
        try:
            # Get initial counts for verification
            initial_user_count = self.User.objects.count()
            initial_custom_user_count = CustomUser.objects.count()
            
            # Ensure transaction rollback for this test
            with transaction.atomic():
                response = self.client.post(reverse('delete_account'), {
                    'confirmation': 'DELETE',
                    'password': 'testpass123'
                })
                
                # Verify redirect to confirmation page
                self.assertEqual(response.status_code, 302)
                
                # Verify account was deleted from both User and CustomUser models
                self.assertEqual(self.User.objects.count(), initial_user_count - 1)
                self.assertEqual(CustomUser.objects.count(), initial_custom_user_count - 1)
                
                # Check specific user is gone
                self.assertFalse(self.User.objects.filter(username='testuser').exists())
                self.assertFalse(CustomUser.objects.filter(user__username='testuser').exists())
                
                # Verification should fail and trigger rollback
                self.fail("Rolling back transaction - test completed successfully")
        except self.failureException as e:
            if str(e) == "Rolling back transaction - test completed successfully":
                # Test passed, but we're rolling back the transaction
                pass
            else:
                raise
        except NoReverseMatch:
            self.skipTest("Account deletion URL not configured yet")

    @unittest.skip("Consent tracking not implemented yet")
    def test_consent_tracking(self):
        """Test that user consent is requested and tracked"""
        try:
            # Test consent checkbox on registration form
            response = self.client.get(reverse('register'))
            self.assertContains(response, 'consent')
            self.assertContains(response, 'type="checkbox"')
            
            # Test registration with consent
            with transaction.atomic():
                response = self.client.post(reverse('register'), {
                    'username': 'consentuser',
                    'password1': 'securepwd123',
                    'password2': 'securepwd123',
                    'email': 'consent@example.com',
                    'gdpr_consent': True
                })
                self.assertEqual(response.status_code, 302)
                
                # Verify consent was stored
                new_user = self.User.objects.get(username='consentuser')
                custom_user = CustomUser.objects.get(user=new_user)
                self.assertTrue(hasattr(custom_user, 'gdpr_consent'))
                self.assertTrue(custom_user.gdpr_consent)
                
                # Cancel transaction to clean up
                self.fail("Rolling back transaction - test completed successfully")
        except self.failureException as e:
            if str(e) == "Rolling back transaction - test completed successfully":
                # Test passed, but we're rolling back the transaction
                pass
            else:
                raise
        except NoReverseMatch:
            self.skipTest("Registration URL not configured yet")
    
    def test_data_minimization(self):
        """Test that only necessary data is collected per GDPR requirements"""
        # Get the custom user for testing
        custom_user = CustomUser.objects.get(user=self.test_user)
        
        # Define necessary fields based on application requirements
        necessary_fields = [
            'id',
            'user', 'cups_saved', 'most_recent_shop_id', 
            'default_badge_id', 'last_active_date_time',
            'streak', 'streak_start_day'
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
