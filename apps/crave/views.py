from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from .models import CraveVideo, VideoLike, VideoReport
from .serializers import CraveVideoSerializer, VideoLikeSerializer, VideoReportSerializer
from apps.seller.models import Shop

# List all videos
class CraveVideoListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        videos = CraveVideo.objects.all().order_by('-created_at')
        serializer = CraveVideoSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data)


# Upload video (only seller with a shop)
class CraveVideoCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            shop = request.user.shop  # OneToOneField from seller to shop
        except Shop.DoesNotExist:
            return Response({"error": "You do not have a shop."}, status=400)

        serializer = CraveVideoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(shop=shop)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# Like or Unlike a video
class ToggleVideoLikeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, video_id):
        video = get_object_or_404(CraveVideo, id=video_id)
        like, created = VideoLike.objects.get_or_create(user=request.user, video=video)
        if not created:
            like.delete()
            return Response({"liked": False}, status=200)
        return Response({"liked": True}, status=201)


# Report a video
class ReportVideoAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VideoReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Video reported successfully."}, status=201)
        return Response(serializer.errors, status=400)
