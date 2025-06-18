from rest_framework import serializers
from .models import Shop, ShopImage, ShopDocument

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'
        read_only_fields = ['owner']


class ShopImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopImage
        fields = '__all__'
        read_only_fields = ['shop']


class ShopDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopDocument
        fields = '__all__'
        read_only_fields = ['shop']