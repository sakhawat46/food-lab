from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, OrderFeedback
from apps.product.models import Product
# from .serializers import OrderSerializer, OrderFeedbackSerializer
from .serializers import OrderSerializer,OrderFeedbackSerializer,SellerOrderUpadteSerializer,SellerOrderShortSummarySeria
import uuid
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
class CustomerOrderCreateAPIView(APIView):
    def post(self, request):
        user = request.user
        items = request.data.get("items")
        note = request.data.get("note", "")
        payment_method = request.data.get("payment_method", "cash_on_delivery")

        if not items:
            return Response({"error": "No items provided"}, status=400)

        # 🆕 Generate a unique order ID
        generated_order_id = str(uuid.uuid4()).split('-')[0].upper()

        # Create order with generated order_id
        order = Order.objects.create(
            customer=user,
            note=note,
            payment_method=payment_method,
            order_id=generated_order_id
        )

        for item in items:
            product = Product.objects.get(id=item['product_id'])
            OrderItem.objects.create(order=order, product=product, quantity=item['quantity'])

        order.calculate_totals()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class CustomerOrderListAPIView(APIView):
    def get(self, request):
        orders = Order.objects.filter(customer=request.user).order_by('-created_at')
        return Response(OrderSerializer(orders, many=True).data)


class SellerOrderListAPIView(APIView):
    def get(self, request):
        if request.user.user_type != 'seller':
            return Response({'error': 'Unauthorized'}, status=403)

        seller_products = Product.objects.filter(seller=request.user)
        order_ids = OrderItem.objects.filter(product__in=seller_products).values_list('order_id', flat=True)
        orders = Order.objects.filter(id__in=order_ids).distinct()

        status_filter = request.GET.get("status")
        if status_filter:
            orders = orders.filter(status=status_filter)

        return Response(OrderSerializer(orders, many=True).data)

# class CustomerUpdateOrderAPIView(APIView):
#     def post(self,request,order_id):
#         order=get_object_or_404(Order,id=order_id,customer_id=request.user.id)
#         items=request.data.get("items")
#         note=request.data.get("note","")
#         payment_method=request.data.get("payment_method","FirstPay")
#         if not items:
#             return Response({"error": "No items provided"}, status=400)

class OrderFeedbackSubmitAPIView(APIView):
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        if hasattr(order, 'feedback'):
            return Response({"error": "Feedback already submitted."}, status=400)

        serializer = OrderFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(order=order)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'seller'  # Adjust this check as per your user model

class SellerOrderUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = SellerOrderUpadteSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        # Allow only sellers to update orders they received
        return Order.objects.filter(customer__isnull=False)  # Or filter by seller’s products if linked

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    

class SellerOrderSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        seller = request.user

        if seller.user_type != 'seller':
            return Response({"error": "Only sellers can access this."}, status=403)

        # Step 1: Get order IDs where the seller owns a product in the order
        order_ids = OrderItem.objects.filter(
            product__seller=seller
        ).values_list('order_id', flat=True).distinct()

        # Step 2: Fetch only those orders
        orders = Order.objects.filter(id__in=order_ids)

        # Step 3: Organize into status categories
        status_keys = ['pending', 'approved', 'completed']
        summary = {key: [] for key in status_keys}

        for key in status_keys:
            filtered_orders = orders.filter(status=key)
            serializer = SellerOrderShortSummarySeria(filtered_orders, many=True)
            summary[key] = serializer.data

        return Response(summary)

    



