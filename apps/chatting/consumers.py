from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import ChatRoom, ChatMessage
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        User = get_user_model()
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_id = data['sender_id']

        sender = await self.get_user(sender_id)
        room = await self.get_room(self.room_id)
        chat = await self.create_message(room, sender, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': chat.message,
                'sender': sender.email,
                'timestamp': str(chat.timestamp)
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_user(self, user_id):
        User = get_user_model()
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def get_room(self, room_id):
        return ChatRoom.objects.get(id=room_id)

    @database_sync_to_async
    def create_message(self, room, sender, message):
        return ChatMessage.objects.create(room=room, sender=sender, message=message)
