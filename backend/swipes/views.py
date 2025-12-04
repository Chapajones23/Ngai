from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Swipe, Match
from users.models import ChatRoom
from .serializers import SwipeSerializer, MatchSerializer
from users.serializers import UserSerializer
import math

User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def swipe_action(request):
    to_user_id = request.data.get('to_user_id')
    action = request.data.get('action')
    
    if action not in ['like', 'dislike', 'superlike']:
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        to_user = User.objects.get(id=to_user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if to_user == request.user:
        return Response({'error': 'Cannot swipe yourself'}, status=status.HTTP_400_BAD_REQUEST)
    
    swipe, created = Swipe.objects.get_or_create(
        from_user=request.user,
        to_user=to_user,
        defaults={'action': action}
    )
    
    if not created:
        swipe.action = action
        swipe.save()
    
    is_match = False
    if action in ['like', 'superlike']:
        reverse_swipe = Swipe.objects.filter(
            from_user=to_user,
            to_user=request.user,
            action__in=['like', 'superlike']
        ).first()
        
        if reverse_swipe:
            user1, user2 = sorted([request.user, to_user], key=lambda u: u.id)
            match, _ = Match.objects.get_or_create(user1=user1, user2=user2)
            ChatRoom.objects.get_or_create(user1=user1, user2=user2)
            is_match = True
    
    return Response({
        'swipe': SwipeSerializer(swipe).data,
        'is_match': is_match
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_matches(request):
    matches = Match.objects.filter(Q(user1=request.user) | Q(user2=request.user))
    serializer = MatchSerializer(matches, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_suggestions(request):
    swiped_user_ids = Swipe.objects.filter(from_user=request.user).values_list('to_user_id', flat=True)
    
    candidates = User.objects.exclude(id=request.user.id).exclude(id__in=swiped_user_ids).exclude(is_banned=True)
    
    if request.user.latitude and request.user.longitude:
        candidates = [user for user in candidates if user.latitude and user.longitude]
        
        scored_candidates = []
        for user in candidates:
            score = calculate_match_score(request.user, user)
            scored_candidates.append((user, score))
        
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        candidates = [user for user, score in scored_candidates[:20]]
    else:
        candidates = candidates[:20]
    
    serializer = UserSerializer(candidates, many=True)
    return Response(serializer.data)

def calculate_match_score(user1, user2):
    score = 0
    
    if user1.latitude and user1.longitude and user2.latitude and user2.longitude:
        distance = calculate_distance(
            user1.latitude, user1.longitude,
            user2.latitude, user2.longitude
        )
        distance_score = max(0, 100 - distance)
        score += distance_score * 0.4
    
    common_interests = set(user1.interests or []) & set(user2.interests or [])
    interest_score = len(common_interests) * 10
    score += interest_score * 0.3
    
    activity_score = 50 if user2.last_active else 0
    score += activity_score * 0.3
    
    return score

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance