from django.test import TestCase
from django.urls import reverse
from EcoffeeBase.models import *

class ShopFormTest(TestCase):
    def test_create_shop_when_submitting_valid_form(self):
        form_data={
            'activeCode':'0003',
            'shopName':'testshop'
        }
        response=self.client.post(reverse('add_shop'),data=form_data)
        self.assertEqual(response.status_code,302)
        self.assertTrue(Shop.objects.filter(shopName='testshop').exists())

    def test_dont_create_shop_when_submitting_invalid_form(self):
        form_data={
            'activeCode':'45738',
            'shopName':'testshop'
        }
        response=self.client.post(reverse('add_shop'),data=form_data)
        self.assertEqual(response.status_code,200)
        self.assertTrue("form" in response.context)
        form=response.context['form']
        self.assertFormError(form,'activeCode','Active code must be between 0 and 9999')
        self.assertFalse(Shop.objects.exists())
    
    def test_dont_create_Shop_when_submitting_repeat_name_invalid_form(self):
        self.shop = Shop.objects.create(
            shopName='testshop',
            activeCode = '1000'
        )
        form_data={
            'activeCode':'1000',
            'shopName':'testshop'
        }
        response=self.client.post(reverse('add_shop'),data=form_data)
        self.assertEqual(response.status_code,200)
        self.assertTrue("form" in response.context)
        form=response.context['form']
        self.assertFormError(form,'shopName','Shop name already exists, please choose a different one')
        self.assertFormError(form,'activeCode','A shop is already using that active code')
        self.assertFalse(len(Shop.objects.all())==2)


class CoffeeFormTest(TestCase):
    def test_create_coffee_when_submitting_valid_form(self):
        form_data={
            'name':'coffee'
        }
        response=self.client.post(reverse('add_coffee'),data=form_data)
        self.assertEqual(response.status_code,302)
        self.assertTrue(Coffee.objects.filter(name='coffee').exists())

    def test_dont_create_coffee_when_repeat_name_invalid_form(self):
        self.coffee = Coffee.objects.create(
            name='coffee',
            numberOrdered=0,
            lastOrdered=None
        )
        form_data={
            'name':'coffee'
        }
        response=self.client.post(reverse('add_coffee'),data=form_data)
        self.assertEqual(response.status_code,200)
        self.assertTrue("form" in response.context)
        form=response.context['form']
        self.assertFormError(form,'name','Coffee name already exists, please choose a different one')
        self.assertFalse(len(Coffee.objects.all())==2)


class BadgeFormTest(TestCase):
    def test_create_badge_when_submitting_valid_form(self):
        form_data={
            'coffeeUntilEarned':'35'
        }
        response=self.client.post(reverse('add_badge'),data=form_data)
        self.assertEqual(response.status_code,302)
        self.assertTrue(Badge.objects.filter(coffeeUntilEarned='35').exists())

    def test_dont_create_badge_when_submitting_repeat_coffeeUntilEarned_invalid_form(self):
        self.badge = Badge.objects.create(
            coffeeUntilEarned='35'
        )
        form_data={
            'coffeeUntilEarned':'35'
        }
        response=self.client.post(reverse('add_badge'),data=form_data)
        self.assertEqual(response.status_code,200)
        self.assertTrue("form" in response.context)
        form=response.context['form']
        self.assertFormError(form,'coffeeUntilEarned','Badge already exists for those number of coffees, please choose a different one')
        self.assertFalse(len(Badge.objects.all())==2)


