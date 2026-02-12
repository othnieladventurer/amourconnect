from django.urls import path
from . import views



app_name = "nmdashboard"


urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my_profiel/', views.my_profile, name='my_profile'),
    path("like/", views.like_or_pass, name="like_or_pass"),
    path("profil/<int:user_id>/", views.voir_profil, name="voir_profil"),
    path("<int:user_id>/", views.chat_view, name="chat"),
    path("unmatch/", views.unmatch_user, name="unmatch_user"),
    path("block/", views.block_user, name="block_user"),


]