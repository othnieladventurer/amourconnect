from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfilePicture


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password1",
            "password2",
            "birth_date",     
            "gender",
            "interested_in",
            "location",
            "bio",
            "profile_photo",
        ]





class UserProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfilePicture
        fields = ['image']



