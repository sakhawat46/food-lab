from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CartItem
from .serializers import CartItemSerializer
from apps.product.models import Product
from apps.order.models import Order, OrderItem
from decimal import Decimal
import uuid
from django.http import HttpResponse, HttpResponseNotFound, Http404
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
def generate_unique_order_id():
    return str(uuid.uuid4()).replace('-', '')[:20]

class CartListView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user).select_related('product')

        if not cart_items.exists():
            return self.error_response(
                message="Your cart is empty",
                data={"products": []},
                status_code=status.HTTP_404_NOT_FOUND
            )

        subtotal = Decimal('0.00')
        product_list = []

        for item in cart_items:
            item_total = item.product.price * item.quantity
            subtotal += item_total
            product_list.append({
                "cart_id": item.id,
                "product_id": item.product.id,
                "name": item.product.name,
                "price": str(item.product.price),
                "quantity": item.quantity,
                "item_total": str(item_total)
            })

        VAT_RATE = Decimal('0.10')
        DELIVERY_FEE = Decimal('50.00')
        vat = subtotal * VAT_RATE
        grand_total = subtotal + vat + DELIVERY_FEE

        return self.success_response(
            message="Cart fetched successfully",
            data={
                "products": product_list,
                "subtotal": str(subtotal),
                "vat": str(vat),
                "delivery_fee": str(DELIVERY_FEE),
                "grand_total": str(grand_total)
            }
        )


class CartItemAddUpdateView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        items = request.data.get('items', [])

        if not isinstance(items, list) or not items:
            return self.error_response(
                message="Provide a valid list of items",
                data={},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        first_product_id = items[0].get("product")
        try:
            first_product = Product.objects.get(id=first_product_id)
        except Product.DoesNotExist:
            return self.error_response(
                message=f"Product {first_product_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        current_seller = first_product.seller

        # 🔒 Ensure only one seller's products in cart
        existing_items = CartItem.objects.filter(user=user)
        if existing_items.exists():
            existing_seller = existing_items.first().product.seller
            if existing_seller != current_seller:
                existing_items.delete()

        responses = []
        subtotal = Decimal('0.00')

        for item in items:
            product_id = item.get('product')
            quantity = int(item.get('quantity', 1))

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                responses.append({'error': f'Product {product_id} not found'})
                continue

            if product.seller != current_seller:
                responses.append({'error': f'Product {product_id} from another seller. Skipped.'})
                continue

            cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
            if not created:
                cart_item.quantity += quantity
            else:
                cart_item.quantity = quantity
            cart_item.save()

            item_total = product.price * cart_item.quantity
            subtotal += item_total

            responses.append({
                'product': product.id,
                'product_name': product.name,
                'price': str(product.price),
                'quantity': cart_item.quantity,
                'item_total': str(item_total)
            })

        VAT_RATE = Decimal('0.10')
        DELIVERY_FEE = Decimal('50.00')
        vat = subtotal * VAT_RATE
        grand_total = subtotal + vat + DELIVERY_FEE

        return self.success_response(
            message="Cart updated successfully",
            data={
                'cart_items': responses,
                'subtotal': str(subtotal),
                'vat': str(vat),
                'delivery_fee': str(DELIVERY_FEE),
                'grand_total': str(grand_total)
            }
        )


class CartItemIncreaseView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        try:
            cart_item = CartItem.objects.get(pk=pk, user=user)
            cart_item.quantity += 1
            cart_item.save()
            return self.success_response(
                message="Quantity increased",
                data={"quantity": cart_item.quantity}
            )
        except CartItem.DoesNotExist:
            return self.error_response(
                message="Cart item not found",
                status_code=status.HTTP_404_NOT_FOUND
            )


class CartItemDecreaseView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        try:
            cart_item = CartItem.objects.get(pk=pk, user=user)
            
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                return self.success_response(
                    message="Quantity decreased",
                    data={"quantity": cart_item.quantity}
                )
            else:
                cart_item.delete()
                return self.success_response(
                    message="Item removed from cart",
                    data={}
                )
        
        except CartItem.DoesNotExist:
            return self.error_response(
                message="Cart item not found",
                status_code=status.HTTP_404_NOT_FOUND
            )



class CartItemDeleteView(BaseAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return self.success_response(
                message="Item deleted from cart",
                data={},
                status_code=status.HTTP_200_OK
            )
        except Http404:
            return self.error_response(
                message="Cart item not found",
                status_code=status.HTTP_404_NOT_FOUND
            )



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from decimal import Decimal
import uuid
import stripe
import json

from django.conf import settings
from .models import CartItem
from apps.order.models import Order,OrderItem
from apps.product.models import Product
from django.contrib.auth import get_user_model

stripe.api_key = settings.STRIPE_SECRET_KEY

class CheckoutView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return self.error_response(
                message="Cart is empty",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        payment_method = request.data.get("payment_method", "cash_on_delivery")
        note = request.data.get("note", "")

        items = []
        total = Decimal("0.00")

        for item in cart_items:
            item_total = item.get_total_price()
            total += item_total
            items.append({
                "product_id": item.product.id,
                "quantity": item.quantity
            })

        TAX_RATE = Decimal('0.10')
        DELIVERY_FEE = Decimal('50.00')
        tax = total * TAX_RATE
        grand_total = total + tax + DELIVERY_FEE

        if payment_method == "cash_on_delivery":
            order = Order.objects.create(
                customer=user,
                order_id=generate_unique_order_id(),
                payment_method='cash_on_delivery',
                note=note,
                status='pending',
                total_price=total,
                tax=tax,
                delivery_fee=DELIVERY_FEE,
                grand_total=grand_total,
                payment_status='unpaid'
            )

            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

            cart_items.delete()

            return self.success_response(
                message="Order created successfully",
                data={
                    "order_id": order.id,
                    "note": order.note,
                    "total": str(total),
                    "tax": str(tax),
                    "delivery_fee": str(DELIVERY_FEE),
                    "grand_total": str(grand_total)
                },
                status_code=status.HTTP_201_CREATED
            )

        elif payment_method == "stripe":
            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    mode='payment',
                    success_url='https://example.com/success',  # 🔁 Update these
                    cancel_url='https://example.com/cancel',
                    customer_email=user.email,
                    line_items=[
                        {
                            'price_data': {
                                'currency': 'usd',
                                'unit_amount': int(grand_total * 100),  # Convert to cents
                                'product_data': {
                                    'name': 'Cart Total Payment',
                                },
                            },
                            'quantity': 1,
                        }
                    ],
                    metadata={
                        "user_id": str(user.id),
                        "note": note,
                        "items": json.dumps(items)
                    }
                )
                return self.success_response(
                    message="Stripe Checkout session created",
                    data={
                        "checkout_url": session.url,
                        "session_id": session.id
                    }
                )

            except Exception as e:
                return self.error_response(
                    message="Stripe session creation failed",
                    data={"error": str(e)},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        else:
            return self.error_response(
                message="Invalid payment method",
                status_code=status.HTTP_400_BAD_REQUEST
            )


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import CartItem
from apps.order.models import Order,OrderItem
from apps.product.models import Product
import stripe
import json
import uuid
import logging
from django.utils.decorators import method_decorator
stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)
User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(BaseAPIView):

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            logger.info(f" Stripe event received: {event['type']}")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f" Signature verification failed: {e}")
            return self.error_response("Invalid signature", status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f" Webhook processing error: {e}")
            return self.error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            metadata = session.get('metadata', {})

            user_id = metadata.get("user_id")
            note = metadata.get("note", "")
            items_json = metadata.get("items", "[]")

            if not user_id:
                logger.error(" Missing user_id in metadata")
                return self.error_response("Missing user_id", status_code=400)

            try:
                items = json.loads(items_json)
            except json.JSONDecodeError as e:
                logger.error(f" Invalid items JSON: {e}")
                return self.error_response("Invalid items format", status_code=400)

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.error(f" User not found: {user_id}")
                return self.error_response("User not found", status_code=404)

            try:
                order = Order.objects.create(
                    customer=user,
                    note=note,
                    payment_method='stripe',
                    payment_status='paid',
                    stripe_payment_intent_id=session.get("payment_intent"),
                    order_id=str(uuid.uuid4()).split('-')[0].upper()
                )
                logger.info(f" Order created: {order.order_id}")

                for item in items:
                    product_id = item.get('product_id')
                    quantity = int(item.get('quantity', 1))

                    try:
                        product = Product.objects.get(id=product_id)
                        OrderItem.objects.create(order=order, product=product, quantity=quantity)
                        logger.info(f" Added product to order: {product.name} x{quantity}")
                    except Product.DoesNotExist:
                        logger.warning(f" Product not found (skipped): {product_id}")

                order.calculate_totals()
                CartItem.objects.filter(user=user).delete()
                logger.info(f" Cart cleared and totals calculated for order {order.order_id}")

            except Exception as e:
                logger.error(f" Error during order creation: {e}")
                return self.error_response("Order creation failed", status_code=500)

        else:
            logger.info(f"ℹ Stripe event ignored: {event['type']}")

        return self.success_response("Webhook processed successfully", status_code=200)





class stripe_weebhook(APIView):

    def post(requset,self):
        user=requset.user

        cartitems=CartItem.objects.filter(user=user)
