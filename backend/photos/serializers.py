from rest_framework import serializers
from .models import Photo, PhotoVerification

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'
        read_only_fields = ['user', 'status', 'created_at', 'updated_at']

class PhotoVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoVerification
        fields = '__all__'
        read_only_fields = ['user', 'status', 'verification_score', 'verified_at', 'created_at']