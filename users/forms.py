from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfilePicture


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email", "username", "password1", "password2", "gender", "interested_in", "location", "bio", "profile_photo"]







class UserProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfilePicture
        fields = ['image']



