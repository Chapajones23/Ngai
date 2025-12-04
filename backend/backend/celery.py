import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'expire-premium-subscriptions': {
        'task': 'tasks.expire_premium_subscriptions',
        'schedule': crontab(hour=0, minute=0),
    },
    'reset-message-quotas': {
        'task': 'tasks.reset_message_quotas',
        'schedule': crontab(hour=0, minute=0),
    },
}