from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
import os

User = get_user_model()

if not firebase_admin._apps:
    if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_notification(request):
    user_id = request.data.get('user_id')
    title = request.data.get('title')
    body = request.data.get('body')
    data = request.data.get('data', {})
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not user.fcm_token:
        return Response({'error': 'User has no FCM token'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data,
            token=user.fcm_token,
        )
        
        response = messaging.send(message)
        
        return Response({
            'message': 'Notification sent successfully',
            'response': response
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_match_notification(request):
    match_user_id = request.data.get('match_user_id')
    
    try:
        match_user = User.objects.get(id=match_user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not match_user.fcm_token:
        return Response({'error': 'User has no FCM token'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title='New Match! 💕',
                body=f'You matched with {request.user.username}!',
            ),
            data={
                'type': 'match',
                'user_id': str(request.user.id),
                'username': request.user.username
            },
            token=match_user.fcm_token,
        )
        
        response = messaging.send(message)
        
        return Response({
            'message': 'Match notification sent',
            'response': response
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message_notification(request):
    recipient_id = request.data.get('recipient_id')
    message_content = request.data.get('message')
    
    try:
        recipient = User.objects.get(id=recipient_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not recipient.fcm_token:
        return Response({'error': 'User has no FCM token'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=f'Message from {request.user.username}',
                body=message_content[:100],
            ),
            data={
                'type': 'message',
                'sender_id': str(request.user.id),
                'sender_username': request.user.username
            },
            token=recipient.fcm_token,
        )
        
        response = messaging.send(message)
        
        return Response({
            'message': 'Message notification sent',
            'response': response
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)