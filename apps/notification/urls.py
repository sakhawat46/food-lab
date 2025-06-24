from django.urls import path
from .views import NotificationListAPIView, MarkNotificationReadAPIView, DeviceTokenRegisterAPIView

urlpatterns = [
    path('notifications/', NotificationListAPIView.as_view(), name='notification-list'),
    path('read/<int:pk>/', MarkNotificationReadAPIView.as_view(), name='notification-read'),
    path('device-token/', DeviceTokenRegisterAPIView.as_view(), name='device-token'),
]
