# shop_dashboard/forms.py
from django import forms
from .models import ShopLogo

class LogoUploadForm(forms.ModelForm):
    class Meta:
        model = ShopLogo
        fields = ['logo']
        widgets = {
            'logo': forms.FileInput(attrs={'accept': 'image/png, image/jpeg'})
        }

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            # 验证文件类型
            valid_extensions = ['png', 'jpg', 'jpeg']
            extension = logo.name.split('.')[-1].lower()
            if extension not in valid_extensions:
                raise forms.ValidationError("仅支持PNG/JPEG格式")
            # 验证文件大小
            if logo.size > 2 * 1024 * 1024:  # 2MB
                raise forms.ValidationError("文件大小不能超过2MB")
        return logo