import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']

        # Reject unauthenticated users
        if not self.user.is_authenticated:
            await self.close()
            return

        # Verify user is a participant in this conversation
        is_participant = await self.check_participant()
        if not is_participant:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Mark messages as read when user connects
        await self.mark_messages_read()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get('message', '').strip()

        if not message_content:
            return

        # Save message to database
        message = await self.save_message(message_content)

        # Broadcast to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'timestamp': message['timestamp'],
                'message_id': message['id'],
            }
        )

    async def chat_message(self, event):
        """Send message to WebSocket client."""
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
            'is_own': event['sender_id'] == self.user.id,
        }))

    @database_sync_to_async
    def check_participant(self):
        try:
            conv = Conversation.objects.get(id=self.conversation_id)
            return self.user in [conv.participant1, conv.participant2]
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        conv = Conversation.objects.get(id=self.conversation_id)
        msg = Message.objects.create(
            conversation=conv,
            sender=self.user,
            content=content,
        )
        # Update conversation timestamp
        conv.save()
        return {
            'id': msg.id,
            'timestamp': msg.timestamp.strftime('%H:%M'),
        }

    @database_sync_to_async
    def mark_messages_read(self):
        Conversation.objects.get(id=self.conversation_id).messages.filter(
            is_read=False
        ).exclude(sender=self.user).update(is_read=True)
