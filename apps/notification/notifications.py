# notifications.py
from pyfcm import FCMNotification
from .models import DeviceToken

def send_firebase_notification(user, title, message):
    try:
        token_obj = DeviceToken.objects.get(user=user)
        push_service = FCMNotification(api_key="YOUR_FIREBASE_SERVER_KEY")

        result = push_service.notify_single_device(
            registration_id=token_obj.token,
            message_title=title,
            message_body=message
        )
        return result
    except DeviceToken.DoesNotExist:
        print("No token found for user")
