from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Coffee

class EcoffeeBaseTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.test_user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.coffee = Coffee.objects.create(
            name='Coffee',
            numberOrdered=0,
            lastOrdered=None
        )

    def test_coffee_creation(self):
        """Test coffee creation"""
        self.assertEqual(self.coffee.name, 'Coffee')
        self.assertEqual(self.coffee.numberOrdered, 0)

