from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoomListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.user_type == 'seller':
            rooms = ChatRoom.objects.filter(seller=user)
        else:
            rooms = ChatRoom.objects.filter(customer=user)
        serializer = ChatRoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        seller_id = request.data.get('seller_id')
        customer_id = request.user.id

        if request.user.user_type != 'customer':
            return Response({"error": "Only customers can initiate chat."}, status=403)
        
        # Validate seller
        try:
            seller = User.objects.get(id=seller_id, user_type='seller')
        except User.DoesNotExist:
            return Response({"error": "Seller not found."}, status=400)

        room, created = ChatRoom.objects.get_or_create(
            customer_id=customer_id,
            seller_id=seller_id
        )
        serializer = ChatRoomSerializer(room)
        return Response(serializer.data, status=201 if created else 200)


class ChatMessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        if request.user not in [room.customer, room.seller]:
            return Response({"error": "Not authorized"}, status=403)

        messages = room.messages.all().order_by('timestamp')
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        if request.user not in [room.customer, room.seller]:
            return Response({"error": "Not authorized"}, status=403)

        data = request.data.copy()
        data['sender'] = request.user.id
        data['room'] = room.id
        serializer = ChatMessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
