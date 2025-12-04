from rest_framework import serializers
from .models import Swipe, Match
from users.serializers import UserSerializer

class SwipeSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)
    
    class Meta:
        model = Swipe
        fields = '__all__'
        read_only_fields = ['from_user', 'created_at']

class MatchSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)
    
    class Meta:
        model = Match
        fields = '__all__'