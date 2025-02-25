from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class LoginSystemTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.test_user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.test_user.save()

    def test_user_creation(self):
        """Test user creation"""
        self.assertEqual(self.test_user.username, 'testuser')
        self.assertEqual(self.test_user.email, 'test@example.com')
        self.assertTrue(self.test_user.check_password('testpass123'))

    def test_login_view(self):
        """Test login view"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authenticate/login.html')

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get(
            'Location'), '/home/')

    def test_login_failure(self):
        """Test failed login"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get(
            'Location'), '/login_system/login_user')

    def test_logout(self):
        """Test logout functionality"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get(
            'Location'), '/login_system/login_user')
