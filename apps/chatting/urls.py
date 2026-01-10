from django.urls import path
from .views import ChatRoomListCreateView, ChatMessageListCreateView

urlpatterns = [
    path('chat/rooms/', ChatRoomListCreateView.as_view(), name='chat-room-list-create'),
    path('chat/messages/<int:room_id>/', ChatMessageListCreateView.as_view(), name='chat-messages'),
]
