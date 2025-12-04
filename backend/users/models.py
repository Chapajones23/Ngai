from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female'), ('other', 'Other')]
    ROLE_CHOICES = [('user', 'User'), ('admin', 'Admin')]
    
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    interests = models.JSONField(default=list, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_updated_at = models.DateTimeField(null=True, blank=True)
    
    is_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    premium_expires_at = models.DateTimeField(null=True, blank=True)
    
    is_banned = models.BooleanField(default=False)
    has_paid_registration = models.BooleanField(default=False)
    
    fcm_token = models.CharField(max_length=500, blank=True)
    
    last_active = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'gender']
    
    def __str__(self):
        return self.email
    
    def update_location(self, lat, lon):
        self.latitude = lat
        self.longitude = lon
        self.location_updated_at = timezone.now()
        self.save()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    height = models.IntegerField(null=True, blank=True)
    education = models.CharField(max_length=100, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    relationship_goal = models.CharField(max_length=50, blank=True)
    drinking = models.CharField(max_length=50, blank=True)
    smoking = models.CharField(max_length=50, blank=True)
    religion = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - Profile"

class Premium(models.Model):
    PLAN_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='premium_subscriptions')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    payment_reference = models.CharField(max_length=100, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.plan}"

class ChatRoom(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatrooms_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatrooms_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user1', 'user2')
    
    def __str__(self):
        return f"Chat: {self.user1.email} - {self.user2.email}"

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.email}: {self.content[:50]}"

class MessageQuota(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='message_quota')
    messages_sent_today = models.IntegerField(default=0)
    last_reset = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.messages_sent_today} messages"

class Ad(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.URLField()
    target_url = models.URLField()
    is_active = models.BooleanField(default=True)
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title