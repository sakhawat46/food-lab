from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Notification, DeviceToken
from .serializers import NotificationSerializer, DeviceTokenSerializer
from .utils import create_notification


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


class NotificationListAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
        serializer = NotificationSerializer(notifications, many=True)
        return self.success_response(
            message="Notifications retrieved successfully.",
            data=serializer.data
        )



class MarkNotificationReadAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return self.success_response(
                message="Notification marked as read."
            )
        except Notification.DoesNotExist:
            return self.error_response(
                message="Notification not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )


class DeviceTokenRegisterAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = DeviceTokenSerializer(data=request.data)
        if serializer.is_valid():
            token, _ = DeviceToken.objects.update_or_create(
                user=request.user,
                defaults={'token': serializer.validated_data['token']}
            )
            return self.success_response(
                message="Device token registered successfully."
            )
        return self.error_response(
            message="Failed to register device token.",
            data=serializer.errors
        )