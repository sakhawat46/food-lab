from rest_framework import serializers
from .models import Shop, ShopImage, ShopDocument, ShopCategory

class ShopSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=ShopCategory.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Shop
        fields = [
            'id', 'owner', 'shop_logo', 'shop_name', 'shop_description',
            'shop_email', 'shop_contact_number',
            'flat_house_number', 'street', 'city', 'postcode',
            'latitude', 'longitude',
            'categories',
        ]
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




class ShopCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopCategory
        fields = ['id', 'name']


class ShopMapSerializer(serializers.ModelSerializer):
    categories = ShopCategorySerializer(many=True)
    class Meta:
        model = Shop
        fields = ['id', 'shop_name', 'latitude', 'longitude', 'categories']



class ShopSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'shop_name'] 