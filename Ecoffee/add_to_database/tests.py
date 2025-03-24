from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import HttpResponseForbidden
from EcoffeeBase.models import ShopUser, Shop, Badge
from .form import ShopForm, BadgeForm

class AddNewDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User=get_user_model()
        cls.regular_user=cls.User.objects.create_user(username='regular',password='password123')
        cls.shop_owner=cls.User.objects.create_user(username='shopowner',password='password123')
        cls.shop=Shop.objects.create(shop_name='Test Shop',active_code='1234')
        cls.shop_user=ShopUser.objects.create(user=cls.shop_owner,shop_id=cls.shop)
        cls.client=Client()


    def test_add_new_data_non_shop_owner(self):
        self.client.login(username='regular',password='password123')
        response=self.client.get(reverse('add_new_data'))
        self.assertEqual(response.status_code,403)


    def test_add_new_data_shop_owner(self):
        self.client.login(username='shopowner',password='password123')
        response = self.client.get(reverse('add_new_data'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'add_new_data.html')
        self.assertIn('shop_form',response.context)
        self.assertIn('badge_form',response.context)


    def test_shop_valid_active_code(self):
        self.client.login(username='shopowner',password='password123')
        response = self.client.post(reverse('add_new_data'),{
            'shop_form_submit':True,
            'active_code':'0001'
        })
        self.shop.refresh_from_db()
        self.assertEqual(self.shop.active_code,'1')
        self.assertRedirects(response,reverse('home'))


    def test_shop_form_invalid_active_code(self):
        self.client.login(username='shopowner',password='password123')
        response=self.client.post(reverse('add_new_data'),{
            'shop_form_submit':True,
            'active_code': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'add_new_data.html')
        self.assertTrue(response.context['shop_form'].errors)

  
    def test_badge_valid_coffees_until_earned(self):
        self.client.login(username='shopowner',password='password123')
        response=self.client.post(reverse('add_new_data'),{
            'badge_form_submit':True,
            'coffee_until_earned':20
        })
        self.assertTrue(Badge.objects.filter(coffee_until_earned=20).exists())
        self.assertRedirects(response,reverse('home'))


    def test_badge_repeat_coffees_until_earned(self):
        self.client.login(username='shopowner',password='password123')
        Badge.objects.create(coffee_until_earned=20)
        response=self.client.post(reverse('add_new_data'),{
            'badge_form_submit':True,
            'coffee_until_earned':20
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'add_new_data.html')
        self.assertTrue(response.context['badge_form'].errors)