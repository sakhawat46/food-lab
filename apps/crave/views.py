from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from .models import CraveVideo, VideoLike, VideoReport
from .serializers import CraveVideoSerializer, VideoLikeSerializer, VideoReportSerializer
from apps.seller.models import Shop



class BaseAPIView(APIView):
    def success_response(self, message="Your request Accepted", data=None, status_code= status.HTTP_200_OK):
        return Response(
            {
            "success": True,
            "message": message,
            "status": status_code,
            "data": data or {}
            },
            status=status_code )
    def error_response(self, message="Your request rejected", data=None, status_code= status.HTTP_400_BAD_REQUEST):
        return Response(
            {
            "success": False,
            "message": message,
            "status": status_code,
            "data": data or {}
            },
            status=status_code )  



# List all videos
class CraveVideoListAPIView(BaseAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        videos = CraveVideo.objects.all().order_by('-created_at')
        serializer = CraveVideoSerializer(videos, many=True, context={'request': request})
        return self.success_response(
            message="Videos retrieved successfully.",
            data=serializer.data
        )


# Upload video (only seller with a shop)
class CraveVideoCreateAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            shop = request.user.shop  # OneToOneField from seller to shop
        except Shop.DoesNotExist:
            return self.error_response(
                message="You do not have a shop.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer = CraveVideoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(shop=shop)
            return self.success_response(
                message="Video uploaded successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Video upload failed.",
            data=serializer.errors
        )



# Like or Unlike a video
class ToggleVideoLikeAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, video_id):
        video = get_object_or_404(CraveVideo, id=video_id)
        like, created = VideoLike.objects.get_or_create(user=request.user, video=video)
        if not created:
            like.delete()
            return self.success_response(
                message="Video unliked.",
                data={"liked": False},
                status_code=status.HTTP_200_OK
            )
        return self.success_response(
            message="Video liked.",
            data={"liked": True},
            status_code=status.HTTP_201_CREATED
        )



# Report a video
class ReportVideoAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VideoReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return self.success_response(
                message="Video reported successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Failed to report video.",
            data=serializer.errors
        )

