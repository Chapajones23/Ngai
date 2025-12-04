from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from photos.models import Photo, PhotoVerification
from users.models import Ad
from photos.serializers import PhotoSerializer, PhotoVerificationSerializer
from users.serializers import AdSerializer, UserSerializer

User = get_user_model()

def is_admin(user):
    return user.role == 'admin'

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_photos(request):
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    photos = Photo.objects.filter(status='pending')
    serializer = PhotoSerializer(photos, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_photo(request, photo_id):
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        photo = Photo.objects.get(id=photo_id)
        photo.status = 'approved'
        photo.save()
        return Response({'message': 'Photo approved', 'photo': PhotoSerializer(photo).data})
    except Photo.DoesNotExist:
        return Response({'error': 'Photo not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_photo(request, photo_id):
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        photo = Photo.objects.get(id=photo_id)
        photo.status = 'rejected'
        photo.save()
        return Response({'message': 'Photo rejected', 'photo': PhotoSerializer(photo).data})
    except Photo.DoesNotExist:
        return Response({'error': 'Photo not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ban_user(request, user_id):
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
        user.is_banned = True
        user.save()
        return Response({'message': 'User banned', 'user': UserSerializer(user).data})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unban_user(request, user_id):
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
        user.is_banned = False
        user.save()
        return Response({'message': 'User unbanned', 'user': UserSerializer(user).data})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_verifications(request):
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    verifications = PhotoVerification.objects.filter(status='pending')
    serializer = PhotoVerificationSerializer(verifications, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_ad(request):
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = AdSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_ads(request):
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    ads = Ad.objects.all()
    serializer = AdSerializer(ads, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_ad(request, ad_id):
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        ad = Ad.objects.get(id=ad_id)
        serializer = AdSerializer(ad, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Ad.DoesNotExist:
        return Response({'error': 'Ad not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_ad(request, ad_id):
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        ad = Ad.objects.get(id=ad_id)
        ad.delete()
        return Response({'message': 'Ad deleted'}, status=status.HTTP_204_NO_CONTENT)
    except Ad.DoesNotExist:
        return Response({'error': 'Ad not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)