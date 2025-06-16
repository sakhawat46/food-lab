from django.contrib import admin
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Profile

admin.site.register(User)
admin.site.register(Profile)