from django import forms
from .models import *


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'banner', 'description', 'category', 'tags', 'read_time']
