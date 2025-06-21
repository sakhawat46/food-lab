from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Shop(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop')
    
    shop_logo = models.ImageField(upload_to='shop_logos/', null=True, blank=True)
    shop_name = models.CharField(max_length=255)
    shop_description = models.TextField()
    shop_email = models.EmailField()
    shop_contact_number = models.CharField(max_length=20)

    flat_house_number = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)

    def __str__(self):
        return self.shop_name


class ShopImage(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='shop_images/')

    def __str__(self):
        return f"Image for {self.shop.shop_name}"



class ShopDocument(models.Model):
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name='documents')

    proof_of_id = models.FileField(upload_to='documents/proof_of_id/', null=True, blank=True)
    right_to_work = models.FileField(upload_to='documents/right_to_work/', null=True, blank=True)
    food_business_registration = models.FileField(upload_to='documents/food_business_registration/', null=True, blank=True)
    hmrc_tax_reference = models.FileField(upload_to='documents/hmrc_tax_reference/', null=True, blank=True)
    allergen_training = models.FileField(upload_to='documents/allergen_training/', null=True, blank=True)
    waste_management = models.FileField(upload_to='documents/waste_management/', null=True, blank=True)
    safety_management = models.FileField(upload_to='documents/safety_management/', null=True, blank=True)

    def __str__(self):
        return f"Documents for {self.shop.shop_name}"




class DriverDocument(models.Model):
    driver = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_documents')

    proof_of_id = models.FileField(upload_to='driver_documents/proof_of_id/', null=True, blank=True)
    right_to_work = models.FileField(upload_to='driver_documents/right_to_work/', null=True, blank=True)
    vehicle = models.FileField(upload_to='driver_documents/vehicle/', null=True, blank=True)
    business_insurance = models.FileField(upload_to='driver_documents/business_insurance/', null=True, blank=True)
    thermal_insulation_kit = models.FileField(upload_to='driver_documents/thermal_insulation_kit/', null=True, blank=True)
    safety_training = models.FileField(upload_to='driver_documents/safety_training/', null=True, blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Driver Documents for {self.driver.email}"