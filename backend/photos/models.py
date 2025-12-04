from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Photo(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    image_url = models.URLField(max_length=500)
    is_primary = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.user.email} - Photo {self.id}"

class PhotoVerification(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('failed', 'Failed'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='photo_verification')
    selfie_url = models.URLField(max_length=500)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    verification_score = models.FloatField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - Verification {self.status}"