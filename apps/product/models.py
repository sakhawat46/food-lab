from django.db import models

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

class Product(models.Model):
    seller = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    dietary_restrictions = models.ManyToManyField(DietaryRestriction, blank=True)
    ingredients = models.TextField(blank=True)
    allergens = models.ManyToManyField(Allergen, blank=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    pre_order = models.BooleanField(default=False)
    always_available = models.BooleanField(default=False)
    pre_order_start = models.DateField(null=True, blank=True)
    pre_order_end = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
