from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Photo, PhotoVerification
from .serializers import PhotoSerializer, PhotoVerificationSerializer
import boto3
import uuid
from django.conf import settings

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_presigned_url(request):
    file_extension = request.query_params.get('file_extension', 'jpg')
    file_name = f"{request.user.id}/{uuid.uuid4()}.{file_extension}"
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    presigned_url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': file_name,
            'ContentType': f'image/{file_extension}'
        },
        ExpiresIn=3600
    )
    
    file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_name}"
    
    return Response({
        'presigned_url': presigned_url,
        'file_url': file_url,
        'file_name': file_name
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_photo(request):
    image_url = request.data.get('image_url')
    is_primary = request.data.get('is_primary', False)
    
    if not image_url:
        return Response({'error': 'Image URL required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if is_primary:
        Photo.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
    
    photo = Photo.objects.create(
        user=request.user,
        image_url=image_url,
        is_primary=is_primary,
        order=Photo.objects.filter(user=request.user).count()
    )
    
    return Response(PhotoSerializer(photo).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_photos(request):
    photos = Photo.objects.filter(user=request.user, status='approved')
    serializer = PhotoSerializer(photos, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_photo(request, photo_id):
    try:
        photo = Photo.objects.get(id=photo_id, user=request.user)
        photo.delete()
        return Response({'message': 'Photo deleted'}, status=status.HTTP_204_NO_CONTENT)
    except Photo.DoesNotExist:
        return Response({'error': 'Photo not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_verification(request):
    selfie_url = request.data.get('selfie_url')
    
    if not selfie_url:
        return Response({'error': 'Selfie URL required'}, status=status.HTTP_400_BAD_REQUEST)
    
    verification, created = PhotoVerification.objects.get_or_create(
        user=request.user,
        defaults={'selfie_url': selfie_url}
    )
    
    if not created:
        verification.selfie_url = selfie_url
        verification.status = 'pending'
        verification.save()
    
    verification_score = perform_liveness_check(selfie_url)
    
    if verification_score > 0.8:
        verification.status = 'verified'
        verification.verification_score = verification_score
        verification.verified_at = timezone.now()
        verification.save()
        
        request.user.is_verified = True
        request.user.save()
        
        return Response({
            'message': 'Verification successful',
            'verification': PhotoVerificationSerializer(verification).data
        })
    else:
        verification.status = 'failed'
        verification.verification_score = verification_score
        verification.save()
        
        return Response({
            'message': 'Verification failed',
            'verification': PhotoVerificationSerializer(verification).data
        }, status=status.HTTP_400_BAD_REQUEST)

def perform_liveness_check(selfie_url):
    return 0.95

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_verification_status(request):
    try:
        verification = PhotoVerification.objects.get(user=request.user)
        return Response(PhotoVerificationSerializer(verification).data)
    except PhotoVerification.DoesNotExist:
        return Response({'status': 'not_started'})