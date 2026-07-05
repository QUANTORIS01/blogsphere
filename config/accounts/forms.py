from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import *


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(max_length=20, widget=forms.PasswordInput(), label='Password', required=True)
    password2 = forms.CharField(max_length=20, widget=forms.PasswordInput(), label='Confirm password', required=True)
    phone = forms.CharField(max_length=11, widget=forms.TextInput(), label='Phone Number', required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

    def clean_password2(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password != password2:
            raise forms.ValidationError('The password does not match the confirmation.')
        return password2

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone:
            if not phone.isnumeric():
                raise forms.ValidationError('The phone number must be a number.')
            if len(phone) != 11:
                raise forms.ValidationError('The phone number must be 11 digits long.')
            if not phone.startswith('09'):
                raise forms.ValidationError('The phone number must start with 09.')
            if User.objects.filter(phone=phone).exists():
                raise forms.ValidationError('The phone number is a duplicate.')
            return phone
        else:
            raise forms.ValidationError('The phone number must not be empty.')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('The username is already taken.')
        return username


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'User Name'}),
                               required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
                               required=True)


class ContactForm(forms.Form):
    SUBJECT_CHOICES = (
        ('Proposal', 'Proposal'),
        ('Criticism', 'Criticism'),
        ('Report', 'Report')
    )
    message = forms.CharField(label='Message text', widget=forms.Textarea, required=True)
    name = forms.CharField(label='Name', max_length=100, required=True)
    phone = forms.CharField(label='Phone Number', max_length=11, required=True)
    email = forms.EmailField(label='Email', required=True)
    subject = forms.ChoiceField(label='Subject', choices=SUBJECT_CHOICES, required=True)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone:
            if not phone.isnumeric():
                raise forms.ValidationError('The phone number must be a number.')
            if len(phone) != 11:
                raise forms.ValidationError('The phone number must be 11 digits long.')
            if not phone.startswith('09'):
                raise forms.ValidationError('The phone number must start with 09.')
            else:
                return phone
        else:
            raise forms.ValidationError('The phone number must not be empty.')