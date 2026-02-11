from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('terms/', views.term_of_use, name='term_of_use'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
]



