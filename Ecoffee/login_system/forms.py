
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserRegistrationForm(forms.ModelForm):
    password1=forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder':'Password'}),
        label='Password'
    )
    password2=forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder':'Re-enter Password'}),
        label='Confirm Password',
        required=True
    )
    email=forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username','email']

    def clean_password2(self):
        password1=self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1!=password2:
            raise ValidationError("Passwords do not match")
        return password2

    def save(self,commit=True):
        user=super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class PasswordResetConfirmForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}),
        label='New Password'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'}),
        label='Confirm Password'
    )
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

