from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date
from .models import Profile, Premium, ChatRoom, Message, MessageQuota, Ad
from .serializers import (UserSerializer, UserRegistrationSerializer, ProfileSerializer,
                          PremiumSerializer, MessageSerializer, ChatRoomSerializer, AdSerializer)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        gender = serializer.validated_data.get('gender')
        if gender == 'male':
            return Response({
                'message': 'Male users must complete payment before registration',
                'requires_payment': True,
                'registration_data': serializer.validated_data
            }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.check_password(password):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if user.is_banned:
        return Response({'error': 'Account banned'}, status=status.HTTP_403_FORBIDDEN)
    
    if user.gender == 'male' and not user.has_paid_registration:
        return Response({'error': 'Payment required', 'requires_payment': True}, 
                       status=status.HTTP_402_PAYMENT_REQUIRED)
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    return Response({
        'user': UserSerializer(user).data,
        'profile': ProfileSerializer(profile).data
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    
    user_data = request.data.get('user', {})
    profile_data = request.data.get('profile', {})
    
    for key, value in user_data.items():
        if hasattr(user, key) and key not in ['id', 'email', 'is_verified', 'is_premium']:
            setattr(user, key, value)
    user.save()
    
    for key, value in profile_data.items():
        if hasattr(profile, key) and key not in ['id', 'user']:
            setattr(profile, key, value)
    profile.save()
    
    return Response({
        'user': UserSerializer(user).data,
        'profile': ProfileSerializer(profile).data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_location(request):
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    if latitude is None or longitude is None:
        return Response({'error': 'Latitude and longitude required'}, status=status.HTTP_400_BAD_REQUEST)
    
    request.user.update_location(latitude, longitude)
    
    return Response({'message': 'Location updated', 'user': UserSerializer(request.user).data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_fcm_token(request):
    token = request.data.get('fcm_token')
    if not token:
        return Response({'error': 'FCM token required'}, status=status.HTTP_400_BAD_REQUEST)
    
    request.user.fcm_token = token
    request.user.save()
    
    return Response({'message': 'FCM token saved'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_rooms(request):
    rooms = ChatRoom.objects.filter(user1=request.user) | ChatRoom.objects.filter(user2=request.user)
    serializer = ChatRoomSerializer(rooms, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, room_id):
    try:
        room = ChatRoom.objects.get(id=room_id)
        if room.user1 != request.user and room.user2 != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        messages = room.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Chat room not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    room_id = request.data.get('room_id')
    content = request.data.get('content')
    
    try:
        room = ChatRoom.objects.get(id=room_id)
        if room.user1 != request.user and room.user2 != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        if not request.user.is_premium:
            quota, _ = MessageQuota.objects.get_or_create(user=request.user)
            if quota.last_reset != date.today():
                quota.messages_sent_today = 0
                quota.last_reset = date.today()
                quota.save()
            
            from django.conf import settings
            if quota.messages_sent_today >= settings.FREE_MESSAGES_PER_DAY:
                return Response({
                    'error': 'Daily message limit reached. Upgrade to premium for unlimited messages.',
                    'requires_premium': True
                }, status=status.HTTP_403_FORBIDDEN)
            
            quota.messages_sent_today += 1
            quota.save()
        
        message = Message.objects.create(
            chat_room=room,
            sender=request.user,
            content=content
        )
        
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Chat room not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ads(request):
    ads = Ad.objects.filter(is_active=True).order_by('?')[:1]
    if ads:
        ad = ads[0]
        ad.impressions += 1
        ad.save()
        return Response(AdSerializer(ad).data)
    return Response(None)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_ad_click(request, ad_id):
    try:
        ad = Ad.objects.get(id=ad_id)
        ad.clicks += 1
        ad.save()
        return Response({'message': 'Click tracked'})
    except Ad.DoesNotExist:
        return Response({'error': 'Ad not found'}, status=status.HTTP_404_NOT_FOUND)