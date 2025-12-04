import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, MessageQuota
from datetime import date
from django.conf import settings

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        has_access = await self.check_room_access()
        if not has_access:
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get('message')
        
        can_send, error = await self.check_message_quota()
        if not can_send:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': error
            }))
            return
        
        message = await self.save_message(message_content)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender_id': self.user.id,
                'sender_name': self.user.username,
                'message_id': message.id,
                'timestamp': message.created_at.isoformat()
            }
        )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp']
        }))
    
    @database_sync_to_async
    def check_room_access(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return room.user1 == self.user or room.user2 == self.user
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def check_message_quota(self):
        if self.user.is_premium:
            return True, None
        
        quota, _ = MessageQuota.objects.get_or_create(user=self.user)
        if quota.last_reset != date.today():
            quota.messages_sent_today = 0
            quota.last_reset = date.today()
            quota.save()
        
        if quota.messages_sent_today >= settings.FREE_MESSAGES_PER_DAY:
            return False, 'Daily message limit reached. Upgrade to premium.'
        
        quota.messages_sent_today += 1
        quota.save()
        return True, None
    
    @database_sync_to_async
    def save_message(self, content):
        room = ChatRoom.objects.get(id=self.room_id)
        message = Message.objects.create(
            chat_room=room,
            sender=self.user,
            content=content
        )
        return message