from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("L'utilisateur doit avoir un email")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)




class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)

    INTEREST_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("everyone", "Everyone"),
    ]
    interested_in = models.CharField(max_length=10, choices=INTEREST_CHOICES, blank=True)

    location = models.CharField(max_length=100, blank=True)
    profile_photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    # NEW FIELDS
    height = models.PositiveIntegerField(null=True, blank=True)  # in cm
    passions = models.TextField(blank=True)  # comma separated passions
    career = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=100, blank=True)
    hobbies = models.TextField(blank=True)
    favorite_music = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


# New model for multiple pictures
class UserProfilePicture(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pictures")
    image = models.ImageField(upload_to="profiles/multiple/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.id}"
