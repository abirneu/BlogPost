from django import forms
from .models import Post, Comment
from django.contrib.auth.models import User
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title','content', 'category','tag']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),

        }
