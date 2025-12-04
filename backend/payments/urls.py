from django.urls import path
from . import views

urlpatterns = [
    path('registration/initiate/', views.initiate_registration_payment, name='initiate_registration_payment'),
    path('subscription/initiate/', views.initiate_subscription_payment, name='initiate_subscription_payment'),
    path('callback/', views.payment_callback, name='payment_callback'),
    path('status/<str:reference>/', views.check_payment_status, name='check_payment_status'),
]