from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Payment
from users.models import Premium, Profile, MessageQuota
import uuid
import requests
import base64
import json
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_registration_payment(request):
    provider = request.data.get('provider')
    phone_number = request.data.get('phone_number')
    registration_data = request.data.get('registration_data', {})
    
    if provider not in ['mpesa', 'tigopesa', 'airtel', 'pesapal']:
        return Response({'error': 'Invalid payment provider'}, status=status.HTTP_400_BAD_REQUEST)
    
    reference = str(uuid.uuid4())
    
    payment = Payment.objects.create(
        payment_type='registration',
        provider=provider,
        amount=settings.REGISTRATION_FEE_MALE,
        phone_number=phone_number,
        reference=reference,
        metadata={'registration_data': registration_data}
    )
    
    if provider == 'mpesa':
        result = initiate_mpesa_payment(phone_number, settings.REGISTRATION_FEE_MALE, reference)
    elif provider == 'tigopesa':
        result = initiate_tigopesa_payment(phone_number, settings.REGISTRATION_FEE_MALE, reference)
    elif provider == 'airtel':
        result = initiate_airtel_payment(phone_number, settings.REGISTRATION_FEE_MALE, reference)
    elif provider == 'pesapal':
        result = initiate_pesapal_payment(phone_number, settings.REGISTRATION_FEE_MALE, reference)
    
    if result.get('success'):
        payment.provider_reference = result.get('provider_reference', '')
        payment.save()
        
        return Response({
            'reference': reference,
            'message': 'Payment initiated',
            'checkout_url': result.get('checkout_url')
        })
    else:
        payment.status = 'failed'
        payment.save()
        return Response({'error': result.get('error', 'Payment initiation failed')}, 
                       status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def payment_callback(request):
    provider = request.data.get('provider')
    reference = request.data.get('reference')
    provider_reference = request.data.get('provider_reference')
    payment_status = request.data.get('status')
    
    try:
        payment = Payment.objects.get(reference=reference)
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    payment.provider_reference = provider_reference
    payment.status = 'completed' if payment_status == 'success' else 'failed'
    payment.save()
    
    if payment.status == 'completed':
        if payment.payment_type == 'registration':
            registration_data = payment.metadata.get('registration_data', {})
            user = User.objects.create_user(
                username=registration_data.get('username'),
                email=registration_data.get('email'),
                password=registration_data.get('password'),
                gender=registration_data.get('gender'),
                date_of_birth=registration_data.get('date_of_birth'),
                has_paid_registration=True
            )
            Profile.objects.create(user=user)
            MessageQuota.objects.create(user=user)
            payment.user = user
            payment.save()
        
        elif payment.payment_type == 'subscription':
            plan_days = {'monthly': 30, 'quarterly': 90, 'yearly': 365}
            plan = payment.metadata.get('plan', 'monthly')
            
            user = payment.user
            user.is_premium = True
            user.premium_expires_at = timezone.now() + timedelta(days=plan_days[plan])
            user.save()
            
            Premium.objects.create(
                user=user,
                plan=plan,
                amount=payment.amount,
                end_date=user.premium_expires_at,
                payment_reference=reference
            )
    
    return Response({'message': 'Callback processed'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_subscription_payment(request):
    provider = request.data.get('provider')
    phone_number = request.data.get('phone_number')
    plan = request.data.get('plan')
    
    plan_prices = {'monthly': 10.00, 'quarterly': 25.00, 'yearly': 90.00}
    
    if plan not in plan_prices:
        return Response({'error': 'Invalid plan'}, status=status.HTTP_400_BAD_REQUEST)
    
    reference = str(uuid.uuid4())
    amount = plan_prices[plan]
    
    payment = Payment.objects.create(
        user=request.user,
        payment_type='subscription',
        provider=provider,
        amount=amount,
        phone_number=phone_number,
        reference=reference,
        metadata={'plan': plan}
    )
    
    if provider == 'mpesa':
        result = initiate_mpesa_payment(phone_number, amount, reference)
    elif provider == 'tigopesa':
        result = initiate_tigopesa_payment(phone_number, amount, reference)
    elif provider == 'airtel':
        result = initiate_airtel_payment(phone_number, amount, reference)
    elif provider == 'pesapal':
        result = initiate_pesapal_payment(phone_number, amount, reference)
    
    if result.get('success'):
        payment.provider_reference = result.get('provider_reference', '')
        payment.save()
        
        return Response({
            'reference': reference,
            'message': 'Payment initiated',
            'checkout_url': result.get('checkout_url')
        })
    else:
        payment.status = 'failed'
        payment.save()
        return Response({'error': result.get('error', 'Payment initiation failed')}, 
                       status=status.HTTP_400_BAD_REQUEST)

def initiate_mpesa_payment(phone_number, amount, reference):
    try:
        auth_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        auth_response = requests.get(
            auth_url,
            auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET)
        )
        access_token = auth_response.json().get('access_token')
        
        stk_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
        ).decode()
        
        payload = {
            'BusinessShortCode': settings.MPESA_SHORTCODE,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': phone_number,
            'PartyB': settings.MPESA_SHORTCODE,
            'PhoneNumber': phone_number,
            'CallBackURL': 'https://yourdomain.com/api/payments/callback/',
            'AccountReference': reference,
            'TransactionDesc': 'Ngai Payment'
        }
        
        response = requests.post(
            stk_url,
            json=payload,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        result = response.json()
        
        if result.get('ResponseCode') == '0':
            return {
                'success': True,
                'provider_reference': result.get('CheckoutRequestID')
            }
        else:
            return {'success': False, 'error': result.get('errorMessage', 'M-Pesa request failed')}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def initiate_tigopesa_payment(phone_number, amount, reference):
    return {'success': True, 'provider_reference': f'TIGO_{reference}'}

def initiate_airtel_payment(phone_number, amount, reference):
    return {'success': True, 'provider_reference': f'AIRTEL_{reference}'}

def initiate_pesapal_payment(phone_number, amount, reference):
    return {
        'success': True,
        'provider_reference': f'PESAPAL_{reference}',
        'checkout_url': f'https://pesapal.com/checkout/{reference}'
    }

@api_view(['GET'])
@permission_classes([AllowAny])
def check_payment_status(request, reference):
    try:
        payment = Payment.objects.get(reference=reference)
        return Response({
            'reference': payment.reference,
            'status': payment.status,
            'amount': payment.amount,
            'provider': payment.provider
        })
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)