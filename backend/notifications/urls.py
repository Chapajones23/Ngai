from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_notification, name='send_notification'),
    path('match/', views.send_match_notification, name='send_match_notification'),
    path('message/', views.send_message_notification, name='send_message_notification'),
]