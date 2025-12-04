from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, Premium, ChatRoom, Message, MessageQuota, Ad

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'gender', 'date_of_birth', 'bio', 'interests', 
                  'latitude', 'longitude', 'is_verified', 'is_premium', 'premium_expires_at',
                  'fcm_token', 'last_active', 'created_at']
        read_only_fields = ['id', 'is_verified', 'is_premium', 'premium_expires_at', 'created_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'gender', 'date_of_birth']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            gender=validated_data['gender'],
            date_of_birth=validated_data.get('date_of_birth')
        )
        Profile.objects.create(user=user)
        MessageQuota.objects.create(user=user)
        return user

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = '__all__'

class PremiumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Premium
        fields = '__all__'
        read_only_fields = ['user', 'start_date', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'chat_room', 'sender', 'sender_name', 'content', 'is_read', 'created_at']
        read_only_fields = ['sender', 'created_at']

class ChatRoomSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'user1', 'user2', 'last_message', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        message = obj.messages.last()
        return MessageSerializer(message).data if message else None

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = '__all__'