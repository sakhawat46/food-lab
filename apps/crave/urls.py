from django.urls import path
from .views import (CraveVideoListAPIView, CraveVideoCreateAPIView, ToggleVideoLikeAPIView, ReportVideoAPIView)

urlpatterns = [
    path('crave/videos/', CraveVideoListAPIView.as_view(), name='crave-video-list'),
    path('crave/videos/upload/', CraveVideoCreateAPIView.as_view(), name='crave-video-upload'),
    path('crave/videos/<int:video_id>/like/', ToggleVideoLikeAPIView.as_view(), name='crave-video-like'),
    path('crave/videos/report/', ReportVideoAPIView.as_view(), name='crave-video-report'),
]
