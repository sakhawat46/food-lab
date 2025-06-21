from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SellerProfile, CustomerProfile
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    mobile_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        # return data

        # Validate mobile number manually here
        self.validate_mobile_number(data['mobile_number'])
        return data
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_mobile_number(self, value):
        if SellerProfile.objects.filter(mobile_number=value).exists() or CustomerProfile.objects.filter(mobile_number=value).exists():
            raise serializers.ValidationError("Mobile number already in use")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        user_type = validated_data.pop('user_type')
        email = validated_data['email']

        user = User.objects.create(
            email=email,
            user_type=user_type,
        )
        user.set_password(password)
        user.save()

        # Create profile
        if user_type == 'seller':
            SellerProfile.objects.create(user=user, name=validated_data['name'], mobile_number=validated_data['mobile_number'])
        else:
            CustomerProfile.objects.create(user=user, first_name=validated_data['name'], mobile_number=validated_data['mobile_number'], last_name="")

        return user




class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("User is inactive")

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_type': user.user_type
        }



class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)




class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        # Generate OTP and send via email
        user.generate_otp()
        print(user.otp)
        # send_mail(
        #     "Password Reset OTP",
        #     f"Your OTP for password reset is {user.otp}",
        #     "sakhawatdev5@gmail.com",  # Change this to your email
        #     [user.email],
        #     fail_silently=False,
        # )
        return value



class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})

        # Check if OTP is correct and not expired
        if user.otp != data["otp"]:
            raise serializers.ValidationError({"otp": "Invalid OTP."})

        if user.otp_exp < now():  # OTP expired
            raise serializers.ValidationError({"otp": "OTP expired."})

        # Mark OTP as verified
        user.otp_verified = True
        user.save()

        return data




class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})

        # Check if OTP was verified
        if not user.otp_verified:
            raise serializers.ValidationError({"otp": "OTP verification required."})

        return data

    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data["email"])
        user.set_password(self.validated_data["new_password"])
        user.otp = None  # Clear OTP after successful reset
        user.otp_exp = None
        user.otp_verified = False  # Reset verification status
        user.save()
        return user
