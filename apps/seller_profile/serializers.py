from rest_framework import serializers
from .models import CompanyDetails, BankDetails, ContactRequest, AccountDeletion

class CompanyDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDetails
        fields = '__all__'
        read_only_fields = ['user_profile']



class BankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetails
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class ContactRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRequest
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class AccountDeletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDeletion
        fields = '__all__'
        read_only_fields = ['user', 'requested_at']