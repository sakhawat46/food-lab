from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMessage

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        room = await self.get_room(self.room_id)
        if not room or self.user not in [room.customer, room.seller]:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message')

            if not message:
                return  # ignore empty messages

            room = await self.get_room(self.room_id)
            if not room or self.user not in [room.customer, room.seller]:
                return  # Unauthorized

            chat = await self.create_message(room, self.user, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': chat.message,
                    'sender': self.user.email,
                    'timestamp': chat.timestamp.isoformat()
                }
            )
        except Exception as e:
            await self.send(json.dumps({'error': str(e)}))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def get_room(self, room_id):
        try:
            return ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def create_message(self, room, sender, message):
        return ChatMessage.objects.create(room=room, sender=sender, message=message)