from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, OrderFeedback
from apps.product.models import Product
# from .serializers import OrderSerializer, OrderFeedbackSerializer
from .serializers import OrderSerializer,OrderFeedbackSerializer,SellerOrderUpadteSerializer,SellerOrderShortSummarySeria
import uuid,stripe,json,logging
from django.conf import settings
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from decimal import Decimal
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
logger = logging.getLogger(__name__)
User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY
from apps.notification.utils import create_notification
# class CustomerOrderCreateAPIView(APIView):
#     def post(self, request):
#         user = request.user
#         items = request.data.get("items")
#         note = request.data.get("note", "")
#         payment_method = request.data.get("payment_method", "cash_on_delivery")

#         if not items:
#             return Response({"error": "No items provided"}, status=400)

#         # 🆕 Generate a unique order ID
#         generated_order_id = str(uuid.uuid4()).split('-')[0].upper()

#         # Create order with generated order_id
#         order = Order.objects.create(
#             customer=user,
#             note=note,
#             payment_method=payment_method,
#             order_id=generated_order_id
#         )

#         for item in items:
#             product = Product.objects.get(id=item['product_id'])
#             OrderItem.objects.create(order=order, product=product, quantity=item['quantity'])

#         order.calculate_totals()

#         return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class BaseAPIView(APIView):
    def success_response(self, message="Your request Accepted", data=None, status_code=status.HTTP_200_OK):
        return Response({
            "success": True,
            "message": message,
            "status": status_code,
            "data": data or {}
        }, status=status_code)

    def error_response(self, message="Your request rejected", data=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            "success": False,
            "message": message,
            "status": status_code,
            "data": data or {}
        }, status=status_code)


class CustomerOrderCreateAPIView(BaseAPIView):
    def post(self, request):
        user = request.user
        items = request.data.get("items")
        note = request.data.get("note", "")
        payment_method = request.data.get("payment_method", "cash_on_delivery")

        if not items:
            return self.error_response("No items provided", status_code=400)

        if payment_method == "cash_on_delivery":
            # 🔷 COD Order
            generated_order_id = str(uuid.uuid4()).split('-')[0].upper()

            order = Order.objects.create(
                customer=user,
                note=note,
                payment_method="cash_on_delivery",
                order_id=generated_order_id
            )

            for item in items:
                try:
                    product = Product.objects.get(id=item['product_id'])
                    quantity = item['quantity']
                    OrderItem.objects.create(order=order, product=product, quantity=quantity)
                except Product.DoesNotExist:
                    return self.error_response(f"Product with id {item['product_id']} not found", status_code=404)

            order.calculate_totals()

            create_notification(
                request.user,
                "Order Created",
                "Your Order has been created successfully Cash On Delevery."
            )
            return self.success_response(
                message="Order placed with Cash on Delivery",
                data={"order_id": order.order_id},
                status_code=status.HTTP_201_CREATED
            )

        elif payment_method == "stripe":
            # 🔷 Stripe Checkout
            line_items = []
            total = Decimal('0.00')

            for item in items:
                try:
                    product = Product.objects.get(id=item['product_id'])
                except Product.DoesNotExist:
                    return self.error_response(f"Product with id {item['product_id']} not found", status_code=404)

                quantity = item['quantity']
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': product.name},
                        'unit_amount': int(product.price * 100),
                    },
                    'quantity': quantity,
                })
                total += product.price * quantity

            DELIVERY_FEE = Decimal('50.00')
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Delivery Fee'},
                    'unit_amount': int(DELIVERY_FEE * 100),
                },
                'quantity': 1,
            })

            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    success_url='http://127.0.0.1:8000/api/v1/products/',
                    cancel_url='http://127.0.0.1:8000/api/v1/products/',
                    metadata={
                        "user_id": str(user.id),
                        "items": json.dumps(items),
                        "note": note
                    }
                )
            except stripe.error.StripeError as e:
                return self.error_response("Stripe error occurred", data={"detail": str(e)}, status_code=500)

            return self.success_response(
                message="Stripe Checkout Session created",
                data={"checkout_url": session.url},
                status_code=status.HTTP_200_OK
            )

        else:
            return self.error_response("Invalid payment method", status_code=400)
@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(BaseAPIView):
    permission_classes = [AllowAny]
    logger = logging.getLogger(__name__)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    def post(self, request):
        User = get_user_model()
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            self.logger.info(f"Stripe Event: {event['type']}")
        except stripe.error.SignatureVerificationError as e:
            self.logger.error(f"Signature verification failed: {e}")
            return self.error_response("Invalid signature", status_code=400)
        except Exception as e:
            self.logger.error(f"Webhook error: {e}")
            return self.error_response(str(e), status_code=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            metadata = session.get('metadata', {})
            user_id = metadata.get("user_id")
            note = metadata.get("note", "")
            items_json = metadata.get("items", "[]")

            if not user_id:
                self.logger.error("Missing user_id in metadata")
                return self.error_response("Missing user_id in metadata", status_code=400)

            try:
                items = json.loads(items_json)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to decode items JSON: {e}")
                items = []

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                self.logger.error(f"User not found: ID {user_id}")
                return self.error_response("User not found", status_code=404)

            try:
                order = Order.objects.create(
                    customer=user,
                    note=note,
                    payment_method='stripe',
                    order_id=str(uuid.uuid4()).split('-')[0].upper(),
                    stripe_payment_intent_id=session.get("payment_intent"),
                    payment_status='paid'
                )
            #     create_notification(
            #     request.user,
            #     "Order Created",
            #     "Your Payment done. Order has been created successfully."
            # )
                self.logger.info(f"Order created: {order.order_id} for user {user_id}")

                for item in items:
                    product_id = item.get('product_id')
                    quantity = item.get('quantity', 1)
                    try:
                        product = Product.objects.get(id=product_id)
                        OrderItem.objects.create(order=order, product=product, quantity=quantity)
                        self.logger.info(f"  Added product {product.name} x{quantity}")
                    except Product.DoesNotExist:
                        self.logger.warning(f" Product not found: ID {product_id}")

                order.calculate_totals()
                self.logger.info(f" Totals calculated for order {order.order_id}")

            except Exception as e:
                self.logger.error(f"Error creating order: {e}")
                return self.error_response("Order creation failed", status_code=500)

            self.logger.info(f"Webhook completed for session {session.get('id')}")
            return self.success_response(message="Stripe webhook handled", status_code=200)

        self.logger.info(f"Ignored event type: {event['type']}")
        return self.success_response(message=f"Ignored event type: {event['type']}", status_code=200)

class CustomerOrderListAPIView(BaseAPIView):
    def get(self, request):
        try:
            orders = Order.objects.filter(customer=request.user).order_by('-created_at')
            serialized_orders = OrderSerializer(orders, many=True).data
            return self.success_response(
                message="Customer orders fetched successfully.",
                data={"orders": serialized_orders},
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return self.error_response(
                message="Failed to fetch customer orders.",
                data={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class SellerOrderListAPIView(BaseAPIView):
    def get(self, request):
        if request.user.user_type != 'seller':
            return self.error_response(
                message="Unauthorized access. Only sellers can view this.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        seller_products = Product.objects.filter(seller=request.user)
        order_ids = OrderItem.objects.filter(product__in=seller_products).values_list('order_id', flat=True)
        orders = Order.objects.filter(id__in=order_ids).distinct()

        status_filter = request.GET.get("status")
        if status_filter:
            orders = orders.filter(status=status_filter)

        serialized_orders = OrderSerializer(orders, many=True)
        return self.success_response(
            message="Orders retrieved successfully.",
            data=serialized_orders.data
        )

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

class SellerOrderUpdateView(BaseAPIView, generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = SellerOrderUpadteSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        # Allow only sellers to update orders they received
        return Order.objects.filter(customer__isnull=False)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', True)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return self.success_response(
                message="Order updated successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return self.error_response(
                message=f"Update failed: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    

class SellerOrderSummaryView(BaseAPIView):  # Inheriting your custom BaseAPIView
    permission_classes = [IsAuthenticated]

    def get(self, request):
        seller = request.user

        if seller.user_type != 'seller':
            return self.error_response(message="Only sellers can access this.", status_code=403)

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

        return self.success_response(
            message="Seller order summary fetched successfully.",
            data=summary
        )

    



