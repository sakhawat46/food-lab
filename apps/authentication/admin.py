from django.contrib import admin
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import SellerProfile, CustomerProfile

admin.site.register(User)
admin.site.register(SellerProfile)
admin.site.register(CustomerProfile)