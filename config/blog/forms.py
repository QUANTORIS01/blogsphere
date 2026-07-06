from django import forms
from .models import *


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'banner', 'description', 'category', 'tags', 'read_time']


class SearchForm(forms.Form):
    query = forms.CharField(label='', max_length=100, required=True)


class AuthorRequestForm(forms.ModelForm):
    class Meta:
        model = AuthorRequest
        fields = ['full_name', 'email', 'phone', 'national_id', 'description', 'resume']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['phone'].widget.attrs['readonly'] = True

    def clean_national_id(self):
        nid = self.cleaned_data['national_id']
        if len(nid) != 10 or not nid.isdigit():
            raise forms.ValidationError('The National ID number is invalid.')
        return nid

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone:
            if not phone.isnumeric():
                raise forms.ValidationError('The phone number must be a number.')
            if len(phone) != 11:
                raise forms.ValidationError('The phone number must be 11 digits long.')
            if phone[0] != '0' and phone[1] != '9':
                raise forms.ValidationError('The phone number must start with 09.')
            else:
                return phone
        else:
            raise forms.ValidationError('The phone number must not be empty.')
