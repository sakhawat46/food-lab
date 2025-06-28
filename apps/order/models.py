# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.authentication.models import User,CustomerProfile
from apps.product.models import Product
from decimal import Decimal
ORDER_STATUS = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('completed', 'Completed'),
    ('rejected', 'Rejected'),
]
Order_Tracking_Status = [
    ('Order placed and confirmed', 'Order placed and confirmed'),
    ('Preparing order', 'Preparing order'),
    ('Order on the way', 'Order on the way'), 
    ('Order Delivered', 'Order Delivered'),
    ('cancelled', 'Cancelled'),
    ('returned', 'Returned'),
]
# class User(AbstractUser):
#     USER_TYPES = (
#         ('customer', 'Customer'),
#         ('seller', 'Seller'),
#     )
#     user_type = models.CharField(max_length=10, choices=USER_TYPES, default='customer')

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    Tracking_Status=models.CharField(max_length=50,choices=Order_Tracking_Status,default='Order placed and confirmed')
    order_id=models.CharField(auto_created=True, max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    note = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='cash_on_delivery')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer}"

    def calculate_totals(self):
        TAX_RATE = Decimal('0.10')
        DELIVERY_FEE = Decimal('50.00')

        item_total = sum(item.get_total_price() for item in self.items.all())
        tax_amount = item_total * TAX_RATE

        self.total_price = item_total
        self.tax = tax_amount
        self.delivery_fee = DELIVERY_FEE
        self.grand_total = item_total + tax_amount + DELIVERY_FEE
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def get_total_price(self):
        from decimal import Decimal
        return Decimal(str(self.product.price)) * Decimal(str(self.quantity))


class OrderFeedback(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='feedback')
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)



