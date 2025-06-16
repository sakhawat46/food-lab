from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    mobile_number = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'name', 'mobile_number']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        name = validated_data.pop('name')
        mobile = validated_data.pop('mobile_number')
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')

        user = User.objects.create_user(password=password, **validated_data)
        Profile.objects.create(user=user, name=name, mobile_number=mobile)
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['user', 'created_at', 'updated_at']
