from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Swipe(models.Model):
    ACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('superlike', 'Super Like'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swipes_made')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swipes_received')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user.email} {self.action} {self.to_user.email}"

class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user1', 'user2')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Match: {self.user1.email} - {self.user2.email}"