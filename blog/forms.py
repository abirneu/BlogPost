from django import forms
from .models import Post, Comment, Profile
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'category', 'tag']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                'placeholder': 'Enter post title...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                'rows': 5
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'post-image-input'
            }),
            'category': forms.Select(attrs={
                'class': 'block w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            }),
            'tag': forms.SelectMultiple(attrs={
                'class': 'block w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            })
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                'rows': 3,
                'placeholder': 'Write your comment...'
            })
        }

class UpdateProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'block w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
        'placeholder': 'Enter your first name'
    }))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'block w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
        'placeholder': 'Enter your last name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'block w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
        'placeholder': 'Enter your email'
    }))
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'rows': 3,
        'placeholder': 'Tell us about yourself...',
        'class': 'block w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100'
    }))
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'hidden',
        'accept': 'image/*',
        'id': 'id_image'
    }))

    class Meta:
        model = Profile
        fields = ['image', 'bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            user = self.instance.user
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['bio'].initial = self.instance.bio
            if self.instance.image:
                self.fields['image'].initial = self.instance.image

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Save user info
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            
            # Save profile
            if self.cleaned_data.get('bio'):
                profile.bio = self.cleaned_data['bio']
            if self.cleaned_data.get('image'):
                profile.image = self.cleaned_data['image']
            profile.save()
        return profile
