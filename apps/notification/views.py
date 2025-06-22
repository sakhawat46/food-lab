from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from .models import DeviceToken
from .serializers import DeviceTokenSerializer
from .firebase import send_firebase_notification
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class DeviceTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeviceTokenSerializer(data=request.data)
        if serializer.is_valid():
            DeviceToken.objects.update_or_create(
                user=request.user,
                defaults={'token': serializer.validated_data['token']}
            )
            return Response({"message": "Token saved successfully"})
        return Response(serializer.errors, status=400)
    



# Example: Call this from an order view
class TriggerNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Let's pretend the seller is being notified
        seller_id = request.data.get("seller_id")  # sent from frontend
        title = request.data.get("title", "New Order")
        message = request.data.get("message", "You have received a new order.")

        try:
            seller = User.objects.get(id=seller_id)
            token_obj = DeviceToken.objects.get(user=seller)
            send_firebase_notification(token_obj.token, title, message)
            return Response({"message": "Notification sent successfully"})
        except User.DoesNotExist:
            return Response({"error": "Seller not found"}, status=404)
        except DeviceToken.DoesNotExist:
            return Response({"error": "Seller has no registered device token"}, status=404)