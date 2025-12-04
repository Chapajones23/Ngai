from django.urls import path
from . import views

urlpatterns = [
    path('swipe/', views.swipe_action, name='swipe_action'),
    path('matches/', views.get_matches, name='get_matches'),
    path('suggestions/', views.get_suggestions, name='get_suggestions'),
]