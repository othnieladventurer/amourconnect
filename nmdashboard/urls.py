from django.urls import path
from . import views



app_name = "nmdashboard"


urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my_profiel/', views.my_profile, name='my_profile'),
    path("like/", views.like_or_pass, name="like_or_pass"),


]