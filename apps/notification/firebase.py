import firebase_admin
from firebase_admin import credentials, messaging

import os

# Load credentials only once
if not firebase_admin._apps:
    cred = credentials.Certificate("D:/Sakhawat/Django_Project/food_lab/food-lab-firebase.json")

    firebase_admin.initialize_app(cred)

def send_firebase_notification(token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )

    response = messaging.send(message)
    return response
