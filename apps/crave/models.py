from django.db import models
from django.conf import settings
from apps.seller.models import Shop

class CraveVideo(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    video = models.FileField(upload_to='crave_videos/')
    thumbnail = models.ImageField(upload_to='crave_thumbnails/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.shop.owner.email}"



class VideoLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video = models.ForeignKey(CraveVideo, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return self.user.email


class VideoReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video = models.ForeignKey(CraveVideo, on_delete=models.CASCADE, related_name='reports')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email