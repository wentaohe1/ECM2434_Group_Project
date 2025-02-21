from django import forms
from EcoffeeBase.models import Coffee

class CoffeeForm (forms.Form):
    coffee_selected=forms.ModelChoiceField(queryset=Coffee.objects.all(),empty_label="Select a coffee")
