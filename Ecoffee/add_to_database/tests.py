from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import HttpResponseForbidden
from EcoffeeBase.models import ShopUser, Shop, Badge
from .form import ShopForm


class AddNewDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.regular_user = cls.User.objects.create_user(
            username='regular', password='password123')
        cls.admin_user = cls.User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="testpassword123"
        )
        cls.shop = Shop.objects.create(
            shop_name='Test Shop', active_code='1234')
        cls.shop_user = ShopUser.objects.create(
            user=cls.admin_user, shop_id=cls.shop)
        cls.client = Client()

    def test_add_new_data_non_shop_owner(self):
        self.client.login(username='regular', password='password123')
        response = self.client.get(reverse('add_shop'))
        self.assertEqual(response.status_code, 302)

    def test_add_new_data_admin(self):
        self.client.login(username='admin', password='testpassword123')
        response = self.client.get(reverse('add_shop'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_shop.html')
        self.assertIn('form', response.context)

    def test_shop_form_invalid_active_code(self):
        self.client.login(username='admin', password='testpassword123')
        response = self.client.post(reverse('add_shop'), {
            'shop_form_submit': True,
            'active_code': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_shop.html')
        self.assertTrue(response.context['form'].errors)
