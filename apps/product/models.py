from django.db import models
from django.contrib.auth import get_user_model
User=get_user_model()
class Cuisine(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class DietaryRestriction(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Allergen(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    image = models.FileField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"

class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    dietary_restrictions = models.ManyToManyField(DietaryRestriction, blank=True)
    ingredients = models.TextField(blank=True)
    allergens = models.ManyToManyField(Allergen, blank=True)
    # image = models.ForeignKey(ProductImage, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_image')

    pre_order = models.BooleanField(default=False)
    always_available = models.BooleanField(default=False)
    pre_order_start = models.DateField(null=True, blank=True)
    pre_order_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class ProductReview(models.Model):
    REPORT_REASONS = [
        ("inappropriate", "Inappropriate language"),
        ("spam", "Spam or promotion"),
        ("fake", "Fake or dishonest review"),
        ("other", "Other"),
    ]
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1 to 5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    seller_reply=models.TextField(blank=True,null=True)
    replyed_at=models.DateTimeField(null=True,blank=True)

    is_reported = models.BooleanField(default=False, blank=True, null=True)
    report_reason = models.CharField(max_length=50, choices=REPORT_REASONS, blank=True, null=True)

    class Meta:
        unique_together = ('product', 'user')  # prevent duplicate reviews

    def __str__(self):
        return f"Review by {self.user} - {self.rating}⭐"


