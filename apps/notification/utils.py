from .models import Notification
from .fcm_service import send_push_notification

def create_notification(user, title, message):
    Notification.objects.create(user=user, title=title, message=message)
    send_push_notification(user, title, message)
