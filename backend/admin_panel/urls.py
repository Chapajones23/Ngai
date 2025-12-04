from django.urls import path
from . import views

urlpatterns = [
    path('photos/pending/', views.get_pending_photos, name='get_pending_photos'),
    path('photos/<int:photo_id>/approve/', views.approve_photo, name='approve_photo'),
    path('photos/<int:photo_id>/reject/', views.reject_photo, name='reject_photo'),
    path('users/<int:user_id>/ban/', views.ban_user, name='ban_user'),
    path('users/<int:user_id>/unban/', views.unban_user, name='unban_user'),
    path('users/', views.get_users, name='get_users'),
    path('verifications/pending/', views.get_pending_verifications, name='get_pending_verifications'),
    path('ads/', views.get_all_ads, name='get_all_ads'),
    path('ads/create/', views.create_ad, name='create_ad'),
    path('ads/<int:ad_id>/update/', views.update_ad, name='update_ad'),
    path('ads/<int:ad_id>/delete/', views.delete_ad, name='delete_ad'),
]