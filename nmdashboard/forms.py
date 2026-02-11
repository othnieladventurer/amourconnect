# nmdashboard/forms.py
from django import forms
from users.models import User, UserProfilePicture

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username", "bio", "birth_date", "gender", "interested_in",
            "location", "profile_photo", "height", "passions", "career",
            "education", "hobbies", "favorite_music",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "bio": forms.Textarea(attrs={"rows":3}),
            "passions": forms.Textarea(attrs={"rows":2}),
            "hobbies": forms.Textarea(attrs={"rows":2}),
            "favorite_music": forms.Textarea(attrs={"rows":2}),
        }

class UserProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfilePicture
        fields = ["image"]




