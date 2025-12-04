from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import Premium, MessageQuota
from datetime import date

User = get_user_model()

@shared_task
def expire_premium_subscriptions():
    now = timezone.now()
    expired_users = User.objects.filter(
        is_premium=True,
        premium_expires_at__lte=now
    )
    
    for user in expired_users:
        user.is_premium = False
        user.save()
        
        Premium.objects.filter(
            user=user,
            is_active=True,
            end_date__lte=now
        ).update(is_active=False)
    
    return f"Expired {expired_users.count()} premium subscriptions"

@shared_task
def reset_message_quotas():
    today = date.today()
    MessageQuota.objects.exclude(last_reset=today).update(
        messages_sent_today=0,
        last_reset=today
    )
    return "Message quotas reset"

@shared_task
def cleanup_old_data():
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=90)
    
    from users.models import Message
    deleted_messages = Message.objects.filter(created_at__lt=cutoff_date).delete()
    
    from swipes.models import Swipe
    deleted_swipes = Swipe.objects.filter(
        created_at__lt=cutoff_date,
        action='dislike'
    ).delete()
    
    return f"Deleted {deleted_messages[0]} messages and {deleted_swipes[0]} swipes"

@shared_task
def send_inactive_user_reminders():
    from datetime import timedelta
    from django.utils import timezone
    
    inactive_threshold = timezone.now() - timedelta(days=7)
    inactive_users = User.objects.filter(
        last_active__lt=inactive_threshold,
        is_banned=False,
        fcm_token__isnull=False
    ).exclude(fcm_token='')
    
    count = 0
    for user in inactive_users:
        count += 1
    
    return f"Sent reminders to {count} inactive users"