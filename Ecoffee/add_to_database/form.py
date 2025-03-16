from django import forms
from EcoffeeBase.models import *

# Describes the django form to that when submitted creates a new shop object in the database


class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ('active_code',)

    # Checks that the active is a unique 4 digit number
    def clean_active_code(self):
        active_code = int(self.cleaned_data.get('active_code'))
        if active_code > 9999 or active_code < 0:
            raise forms.ValidationError(
                'Active code must be between 0 and 9999')
        if Shop.objects.filter(active_code=active_code).exists():
            raise forms.ValidationError(
                'A shop is already using that active code')
        
        
        return active_code



# Describes the django form to that when submitted creates a new badge object in the database
class BadgeForm(forms.ModelForm):
    class Meta:
        model = Badge
        fields = ('coffee_until_earned',)
    # Checks the number of coffees when the badge is earned is unique.

    def clean_coffee_until_earned(self):
        coffee_until_earned = self.cleaned_data.get('coffee_until_earned')
        if Badge.objects.filter(coffee_until_earned=coffee_until_earned).exists():
            raise forms.ValidationError(
                'Badge already exists for those number of coffees, please choose a different one')
        return coffee_until_earned
