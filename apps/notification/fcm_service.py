import firebase_admin
from firebase_admin import credentials, messaging
from .models import DeviceToken

import os
from django.conf import settings

# cred_path = os.path.join(settings.BASE_DIR, 'food-lab-firebase.json')

if not firebase_admin._apps:
    # cred = credentials.Certificate(cred_path)
    # cred = credentials.Certificate("D:/Sakhawat/Django_Project/food_lab/food-lab-firebase.json")
    cred = credentials.Certificate(settings.FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred)

def send_push_notification(user, title, message):
    try:
        device_token = DeviceToken.objects.get(user=user)
    except DeviceToken.DoesNotExist:
        return

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=message
        ),
        token=device_token.token
    )

    try:
        response = messaging.send(message)
        print('Push notification sent:', response)
    except Exception as e:
        print("Error sending push:", e)
