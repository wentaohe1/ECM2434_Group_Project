from django import forms
from EcoffeeBase.models import *

class ShopForm(forms.ModelForm):
    class Meta:
        model=Shop
        fields=('shop_name','active_code')
        
    def clean_activeCode(self):
        active_code=int(self.cleaned_data.get('active_code'))
        if active_code>9999 or active_code<0:
            raise forms.ValidationError('Active code must be between 0 and 9999')
        if Shop.objects.filter(active_code=active_code).exists():
            raise forms.ValidationError('A shop is already using that active code')
        return active_code
    
    def clean_shopName(self):
        shop_name=self.cleaned_data.get('shop_name')
        if Shop.objects.filter(shop_name=shop_name).exists():
            raise forms.ValidationError('Shop name already exists, please choose a different one')
        return shop_name




class BadgeForm(forms.ModelForm):
    class Meta:
        model=Badge
        fields=('coffee_until_earned',)
    def clean_coffeeUntilEarned(self):
        coffee_until_earned=self.cleaned_data.get('coffee_until_earned')
        if Badge.objects.filter(coffee_until_earned=coffee_until_earned).exists():
            raise forms.ValidationError('Badge already exists for those number of coffees, please choose a different one')
        return coffee_until_earned