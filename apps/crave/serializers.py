from rest_framework import serializers
from .models import CraveVideo, VideoLike, VideoReport
from apps.seller.models import Shop

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['owner', 'shop_logo', 'shop_name', 'shop_description', 
                  'shop_email', 'shop_contact_number', 'flat_house_number', 
                  'street', 'city', 'postcode']


class CraveVideoSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)

    class Meta:
        model = CraveVideo
        fields = ['id', 'shop', 'title', 'video', 'thumbnail', 'description', 'created_at', 'likes_count']
        read_only_fields = ['shop', 'likes_count']


class VideoLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoLike
        fields = ['id', 'user', 'video', 'created_at']
        read_only_fields = ['user']


class VideoReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoReport
        fields = ['id', 'user', 'video', 'reason', 'created_at']
        read_only_fields = ['user']
