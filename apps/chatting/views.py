from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()



class BaseAPIView(APIView):
    def success_response(self, message="Your request Accepted", data=None, status_code= status.HTTP_200_OK):
        return Response(
            {
            "success": True,
            "message": message,
            "status": status_code,
            "data": data or {}
            },
            status=status_code )
    def error_response(self, message="Your request rejected", data=None, status_code= status.HTTP_400_BAD_REQUEST):
        return Response(
            {
            "success": False,
            "message": message,
            "status": status_code,
            "data": data or {}
            },
            status=status_code )  



class ChatRoomListCreateView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.user_type == 'seller':
            rooms = ChatRoom.objects.filter(seller=user)
        else:
            rooms = ChatRoom.objects.filter(customer=user)

        serializer = ChatRoomSerializer(rooms, many=True)
        return self.success_response(
            message="Chat rooms retrieved successfully.",
            data=serializer.data
        )

    def post(self, request):
        if request.user.user_type != 'customer':
            return self.error_response(
                message="Only customers can initiate chat.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        seller_id = request.data.get('seller_id')
        customer_id = request.user.id

        try:
            seller = User.objects.get(id=seller_id, user_type='seller')
        except User.DoesNotExist:
            return self.error_response(message="Seller not found.")

        room, created = ChatRoom.objects.get_or_create(
            customer_id=customer_id,
            seller_id=seller_id
        )
        serializer = ChatRoomSerializer(room)
        return self.success_response(
            message="Chat room created." if created else "Chat room already exists.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )



class ChatMessageListCreateView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        if request.user not in [room.customer, room.seller]:
            return self.error_response(
                message="Not authorized to access this chat room.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        messages = room.messages.all().order_by('timestamp')
        serializer = ChatMessageSerializer(messages, many=True)
        return self.success_response(
            message="Messages retrieved successfully.",
            data=serializer.data
        )

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        if request.user not in [room.customer, room.seller]:
            return self.error_response(
                message="Not authorized to send message in this room.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        data = request.data.copy()
        data['sender'] = request.user.id
        data['room'] = room.id

        serializer = ChatMessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                message="Message sent successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Message sending failed.",
            data=serializer.errors
        )
