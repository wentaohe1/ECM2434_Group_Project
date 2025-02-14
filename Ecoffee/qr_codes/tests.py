from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class QRCodeTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.test_user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_qr_code_page_access(self):
        """Test QR code page access"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
