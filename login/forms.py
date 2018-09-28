from django import forms
from .models import User
from captcha.fields import CaptchaField


class UserForm(forms.Form):
    username = forms.CharField(max_length=128, label='用户', widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(max_length=256, label='密码', widget=forms.PasswordInput(attrs={"class": "form-control"}))
    captcha = CaptchaField(label='验证码')


class RegisterForm(forms.Form):
    gender = {
        ("male", "男"),
        ("female", "女")
    }
    username = forms.CharField(max_length=128, label='用户名', widget=forms.TextInput(attrs={"class": "form-control"}))
    password1 = forms.CharField(max_length=256, label='密码', widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(max_length=256, label='确认密码', widget=forms.PasswordInput(attrs={"class": "form-control"}))
    email = forms.EmailField(label='邮箱地址', widget=forms.EmailInput(attrs={"class": "form-control"}))
    sex = forms.ChoiceField(label="性别", choices=gender)
    captcha = CaptchaField(label="验证码")


class UserModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'password']

    def __init__(self, *args, **kwargs):
        super(UserModelForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = '用户名'
        self.fields['password'].label = '密码'
