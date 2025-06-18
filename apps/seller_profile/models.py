from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class CompanyDetails(models.Model):
    user_profile = models.OneToOneField(User,on_delete=models.CASCADE,related_name='company_details')
    trading_name = models.CharField(max_length=100)
    company_registration_number = models.CharField(max_length=20)
    registered_address = models.CharField(max_length=200)
    
    def __str__(self):
        return f"Company details for {self.trading_name}"
    



class BankDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100)
    account_holder_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=8)
    sort_code = models.CharField(max_length=6)
    post_code = models.CharField(max_length=10)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account_holder_name}'s Bank Details"
    


class ContactRequest(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='contact_requests')
    email = models.EmailField(verbose_name="Your Email Address")
    subject = models.CharField(max_length=200, verbose_name="Subject")
    message = models.TextField(verbose_name="Your Message")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Contact from {self.email} about {self.subject}"

class AccountDeletion(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='deletion_requests')
    REASON_CHOICES = [
        ('privacy', 'Privacy concerns'),
        ('service', 'Dissatisfied with service'),
        ('alternative', 'Found alternative service'),
        ('other', 'Other reason'),
    ]
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, verbose_name="Reason", default='other')
    additional_comments = models.TextField(verbose_name="Additional Comments",blank=True,null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Deletion request from {self.user.email}"