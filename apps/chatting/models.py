from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()


class ChatRoom(models.Model):
    customer = models.ForeignKey(User,on_delete=models.CASCADE,limit_choices_to={'user_type': 'customer'},related_name='customer_chatrooms')
    seller = models.ForeignKey(User,on_delete=models.CASCADE,limit_choices_to={'user_type': 'seller'},related_name='seller_chatrooms')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'seller')

    def __str__(self):
        return f"ChatRoom({self.customer.email} ↔ {self.seller.email})"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.email}: {self.message[:30]}..."
