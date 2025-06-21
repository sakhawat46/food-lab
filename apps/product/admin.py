from django.contrib import admin
from .models import Product, Cuisine, DietaryRestriction, Allergen,ProductImage, Order,ProductReview

admin.site.register(Product)
admin.site.register(Cuisine)
admin.site.register(DietaryRestriction)
admin.site.register(Allergen)
admin.site.register(ProductImage)
admin.site.register(ProductReview)