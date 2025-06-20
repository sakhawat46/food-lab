from django.contrib import admin
from .models import CraveVideo, VideoLike, VideoReport

# Register your models here.

admin.site.register(CraveVideo)
admin.site.register(VideoLike)
admin.site.register(VideoReport)