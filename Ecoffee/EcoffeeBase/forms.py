from django import forms
from .models import CustomUser
from django.contrib.auth.models import User

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_image']
        widgets = {
            'profile_image': forms.FileInput(attrs={'id': 'id_profile_image'}),
        }
    
class ChangeUserDetailsForm(forms.ModelForm):
    username=forms.CharField(required=False)
    email=forms.EmailField(required=False)
    password=forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
    )
    class Meta:
        model = User
        fields = ['username','email','password']


    def clean(self):
        cleaned_data=super().clean()
        if not cleaned_data.get("username"):
            cleaned_data["username"]=self.instance.username
        if not cleaned_data.get("email"):
            cleaned_data["email"]=self.instance.email
        if not cleaned_data.get("password"):
            cleaned_data.pop("password",None)
        return cleaned_data


    def save(self, commit=True):
        user=self.instance
        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user