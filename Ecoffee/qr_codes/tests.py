from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from EcoffeeBase.models import *
from urllib.parse import urlencode


class QRCodeTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.test_user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.shop = Shop.objects.create(
            shop_name='testshop',
            active_code='1000'
        )

        self.badge = Badge.objects.create(
            coffee_until_earned='5'
        )

    def test_qr_code_page_access(self):
        """Test QR code page access"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_receive_code_with_valid_shop_code_and_login(self):
        self.client.login(username='testuser', password='testpass123')
        code = '1000'
        url = reverse('receive_code')
        url_with_query = f"{url}?{urlencode({'code': code})}"
        response = self.client.get(url_with_query)
        self.assertEqual(response.headers.get('Location'), '/home/')
        self.assertEqual(Shop.objects.get(
            active_code='1000').number_of_visits, 1)
        self.assertEqual(CustomUser.objects.get(
            user=self.test_user).cups_saved, 1)

    def test_receive_code_with_invalid_shop_code(self):
        self.client.login(username='testuser', password='testpass123')
        code = '16785'
        url = reverse('receive_code')
        url_with_query = f"{url}?{urlencode({'code': code})}"
        response = self.client.get(url_with_query)
        self.assertEqual(response.headers.get('Location'), '/home/')

    def test_receive_code_with_valid_shop_code_not_logged_in(self):
        code = '1000'
        url = reverse('receive_code')
        url_with_query = f"{url}?{urlencode({'code': code})}"
        response = self.client.get(url_with_query)
        self.assertEqual(response.headers.get(
            'Location'), '/login_system/login_user')
        self.assertEqual(Shop.objects.get(
            active_code='1000').number_of_visits, 0)
        self.assertEqual(CustomUser.objects.get(
            user=self.test_user).cups_saved, 0)

    def test_receive_code_with_valid_shop_code_logged_in_update_badge(self):
        self.client.login(username='testuser', password='testpass123')
        code = '1000'
        url = reverse('receive_code')
        url_with_query = f"{url}?{urlencode({'code': code})}"
        response = self.client.get(url_with_query)
        response = self.client.get(url_with_query)
        response = self.client.get(url_with_query)
        response = self.client.get(url_with_query)
        response = self.client.get(url_with_query)

        self.assertEqual(response.headers.get('Location'), '/home/')
        self.assertEqual(Shop.objects.get(
            active_code='1000').number_of_visits, 5)
        self.assertEqual(CustomUser.objects.get(
            user=self.test_user).cups_saved, 5)
        self.assertEqual(CustomUser.objects.get(
            user=self.test_user).default_badge_id, self.badge)
