from django import forms
from EcoffeeBase.models import *

class LogoForm(forms.ModelForm):
    class Meta:
        model=Shop
        fields=('logo',)
        widgets = {
            'logo': forms.FileInput(attrs={'id': 'id_logo_image'}),
        }

class ShopForm(forms.ModelForm):
    class Meta:
        model=Shop
        fields=('shop_name','active_code')
        
    def clean_active_code(self):
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

