from rest_framework import serializers
from .models import User, Product, Order, OrderItem, OrderFeedback
from apps.product.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'status', 'note', 'payment_method',
            'total_price', 'delivery_fee', 'tax', 'grand_total',
            'created_at', 'rejection_reason', 'items'
        ]


class OrderFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderFeedback
        fields = ['id', 'rating', 'comment', 'created_at']



class SellerOrderUpadteSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=["status",'Tracking_Status',"rejection_reason"]

        def validate(self,attrs):
            status=attrs.get('status')
            reason=attrs.get('rejection_reason')

            if status == 'rejected' and not reason:
                raise serializers.ValidationError("Rejection reason is required when order is rejected.")
            return attrs
        
        

