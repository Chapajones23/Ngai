from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('location/update/', views.update_location, name='update_location'),
    path('fcm-token/', views.save_fcm_token, name='save_fcm_token'),
    path('chat/rooms/', views.get_chat_rooms, name='get_chat_rooms'),
    path('chat/messages/<int:room_id>/', views.get_messages, name='get_messages'),
    path('chat/send/', views.send_message, name='send_message'),
    path('ads/', views.get_ads, name='get_ads'),
    path('ads/<int:ad_id>/click/', views.track_ad_click, name='track_ad_click'),
]