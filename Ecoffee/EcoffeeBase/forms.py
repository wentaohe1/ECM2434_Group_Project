from django import forms
from .models import CustomUser

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_image']
        widgets = {
            'profile_image': forms.FileInput(attrs={'id': 'id_profile_image'}),
        }