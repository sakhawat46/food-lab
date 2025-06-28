from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CartItem
from .serializers import CartItemSerializer
from apps.product.models import Product
from apps.order.models import Order, OrderItem
from decimal import Decimal
import uuid

def generate_unique_order_id():
    return str(uuid.uuid4()).replace('-', '')[:20]

class CartListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user).select_related('product')

        if not cart_items.exists():
            return Response({"message": "Your cart is empty", "products": []})

        subtotal = Decimal('0.00')
        product_list = []

        for item in cart_items:
            item_total = item.product.price * item.quantity
            subtotal += item_total
            product_list.append({
                "cart_id": item.id,  # 🆔 Include CartItem ID
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

        return Response({
            "products": product_list,
            "subtotal": str(subtotal),
            "vat": str(vat),
            "delivery_fee": str(DELIVERY_FEE),
            "grand_total": str(grand_total)
        })


class CartItemAddUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        items = request.data.get('items', [])

        if not isinstance(items, list) or not items:
            return Response({'error': 'Provide a list of items'}, status=400)

        first_product_id = items[0].get("product")
        try:
            first_product = Product.objects.get(id=first_product_id)
        except Product.DoesNotExist:
            return Response({"error": f"Product {first_product_id} not found"}, status=404)

        current_seller = first_product.seller

        # 🔒 Check existing cart seller
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

        return Response({
            'cart_items': responses,
            'subtotal': str(subtotal),
            'vat': str(vat),
            'delivery_fee': str(DELIVERY_FEE),
            'grand_total': str(grand_total)
        })


class CartItemIncreaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        try:
            cart_item = CartItem.objects.get(pk=pk, user=user)
            cart_item.quantity += 1
            cart_item.save()
            return Response({'message': 'Quantity increased', 'quantity': cart_item.quantity})
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=404)


class CartItemDecreaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        try:
            cart_item = CartItem.objects.get(pk=pk, user=user)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                return Response({'message': 'Quantity decreased', 'quantity': cart_item.quantity})
            else:
                cart_item.delete()
                return Response({'message': 'Item removed from cart'})
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=404)


class CartItemDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        note = request.data.get("note", "")  # ✅ get note from request

        order_id = generate_unique_order_id()
        while Order.objects.filter(order_id=order_id).exists():
            order_id = generate_unique_order_id()
        # Create the order
        order = Order.objects.create(
            customer=user,
            order_id=order_id,
            payment_method='cash_on_delivery',
            status='pending',
            note=note  # ✅ store note in order
        )

        total = Decimal('0.00')
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )
            total += item.get_total_price()

        TAX_RATE = Decimal('0.10')
        DELIVERY_FEE = Decimal('50.00')
        tax = total * TAX_RATE
        grand_total = total + tax + DELIVERY_FEE

        order.total_price = total
        order.tax = tax
        order.delivery_fee = DELIVERY_FEE
        order.grand_total = grand_total
        order.save()

        cart_items.delete()

        return Response({
            "message": "Order created successfully",
            "order_id": order.id,
            "note": order.note,  # ✅ include note in response (optional)
            "total": total,
            "tax": tax,
            "delivery_fee": DELIVERY_FEE,
            "grand_total": grand_total
        })
