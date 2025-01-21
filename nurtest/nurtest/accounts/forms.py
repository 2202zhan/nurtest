from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Ваше имя пользователя', 'class': 'form-input'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Ваш email', 'class': 'form-input'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Ваш пароль', 'class': 'form-input'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Подтвердите пароль', 'class': 'form-input'})



class CustomUserLoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
