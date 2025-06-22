from django.urls import path
from .views import NotificationListAPIView, TriggerNotificationView, DeviceTokenView

urlpatterns = [
    path('notifications/', NotificationListAPIView.as_view(), name='notification-list'),
    path('save-token/', DeviceTokenView.as_view(), name='save-token'),
    path('send-notification/', TriggerNotificationView.as_view(), name='send-notification'),
]
