from rest_framework import serializers
from .models import Product,OrderItem,Order,ProductImage,ProductReview  # or whatever model you are using

from django.contrib.auth import get_user_model

User = get_user_model()

# ✅ User Serializer for nested representation
class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

# class ProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    image_files = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        exclude = ['seller']

    # def create(self, validated_data):
    #     image_files = validated_data.pop('image_files', [])
    #     product = Product.objects.create(**validated_data, seller=self.context['request'].user)
    #     for image in image_files:
    #         ProductImage.objects.create(product=product, image=image)
    #     return product
    def create(self, validated_data):
        image_files = validated_data.pop('image_files', [])
        dietary_restrictions = validated_data.pop('dietary_restrictions', [])
        allergens = validated_data.pop('allergens', [])

        # Create product WITHOUT M2M fields
        product = Product.objects.create(**validated_data, seller=self.context['request'].user)

    # ✅ Assign M2M after creation
        product.dietary_restrictions.set(dietary_restrictions)
        product.allergens.set(allergens)

    # ✅ Save multiple images
        for image in image_files:
            ProductImage.objects.create(product=product, image=image)

        return product


    def update(self, instance, validated_data):
        image_files = validated_data.pop('image_files', [])
        dietary_restrictions = validated_data.pop('dietary_restrictions', None)
        allergens = validated_data.pop('allergens', None)

        # 🔄 Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # ✅ Handle M2M fields
        if dietary_restrictions is not None:
            instance.dietary_restrictions.set(dietary_restrictions)
        if allergens is not None:
            instance.allergens.set(allergens)

        # ✅ Save new image uploads
        if image_files:
        # Delete old images
            instance.images.all().delete()

        # Save new images
        for image in image_files:
            ProductImage.objects.create(product=instance, image=image)

        return instance

    
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['product', 'product_name', 'quantity', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at', 'items', 'total_price']
        read_only_fields = ['user', 'status', 'created_at']

class ProductReviewSerializerwithReply(serializers.ModelSerializer):
    user=UserPublicSerializer(read_only=True)
    product=serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),required=False)
    class Meta:
        model=ProductReview
        fields=['id','product','user','rating','comment','created_at','seller_reply','replyed_at']
        read_only_fields=['user','created_at','seller_reply','replyed_at']
