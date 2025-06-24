from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Notification, DeviceToken
from .serializers import NotificationSerializer, DeviceTokenSerializer
from .utils import create_notification

class NotificationListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class MarkNotificationReadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"detail": "Marked as read"}, status=200)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=404)


class DeviceTokenRegisterAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = DeviceTokenSerializer(data=request.data)
        if serializer.is_valid():
            token, _ = DeviceToken.objects.update_or_create(
                user=request.user,
                defaults={'token': serializer.validated_data['token']}
            )
            return Response({'detail': 'Device token registered'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
