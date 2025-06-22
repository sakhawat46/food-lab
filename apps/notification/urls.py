from django.urls import path
from .views import NotificationListAPIView
from .views import DeviceTokenView

urlpatterns = [
    path('notifications/', NotificationListAPIView.as_view(), name='notification-list'),
    path('save-token/', DeviceTokenView.as_view(), name='save-token'),
]
