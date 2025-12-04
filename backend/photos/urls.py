from django.urls import path
from . import views

urlpatterns = [
    path('presigned-url/', views.get_presigned_url, name='get_presigned_url'),
    path('upload/', views.upload_photo, name='upload_photo'),
    path('list/', views.get_photos, name='get_photos'),
    path('<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),
    path('verification/submit/', views.submit_verification, name='submit_verification'),
    path('verification/status/', views.get_verification_status, name='get_verification_status'),
]