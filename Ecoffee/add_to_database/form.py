from django import forms
from EcoffeeBase.models import *

class ShopForm(forms.ModelForm):
    class Meta:
        model=Shop
        fields=('shopName','activeCode')
        
    def clean_activeCode(self):
        active_code=int(self.cleaned_data.get('activeCode'))
        if active_code>9999 or active_code<0:
            raise forms.ValidationError('Active code must be between 0 and 9999')
        if Shop.objects.filter(activeCode=active_code).exists():
            raise forms.ValidationError('A shop is already using that active code')
        return active_code
    
    def clean_shopName(self):
        shop_name=self.cleaned_data.get('shopName')
        if Shop.objects.filter(shopName=shop_name).exists():
            raise forms.ValidationError('Shop name already exists, please choose a different one')
        return shop_name


class CoffeeForm(forms.ModelForm):
    class Meta:
        model=Coffee
        fields=('name',)

    def clean_name(self):
        coffee_name=self.cleaned_data.get('name')
        if Coffee.objects.filter(name=coffee_name).exists():
            raise forms.ValidationError('Coffee name already exists, please choose a different one')
        return coffee_name


class BadgeForm(forms.ModelForm):
    class Meta:
        model=Badge
        fields=('coffeeUntilEarned',)
    def clean_coffeeUntilEarned(self):
        coffee_until_earned=self.cleaned_data.get('coffeeUntilEarned')
        if Badge.objects.filter(coffeeUntilEarned=coffee_until_earned).exists():
            raise forms.ValidationError('Badge already exists for those number of coffees, please choose a different one')
        return coffee_until_earned