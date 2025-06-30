from django.contrib.auth import authenticate
from .serializers import SignupSerializer, LoginSerializer, ChangePasswordSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import PasswordResetRequestSerializer, OTPVerificationSerializer, PasswordResetSerializer, MobileOTPRequestSerializer, MobileOTPVerificationSerializer, MobilePasswordResetSerializer, ContactOptionCheckSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import RetrieveUpdateAPIView
from .models import SellerProfile, CustomerProfile
from .serializers import SellerProfileSerializer, CustomerProfileSerializer

from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from .serializers import CustomGoogleLoginSerializer
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter

User = get_user_model()


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token is None:
                response_error = {
                    "success": False,
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Refresh token is required",
                    "errors": {"error": ["Refresh token is required."]},
                }
                return Response(response_error, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            response_data = {
                "success": True,
                "status": status.HTTP_205_RESET_CONTENT,
                "message": "Successfully logged out.",
            }

            return Response(response_data, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            response_error = {
                "success": False,
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Error occured",
                "errors": {"error": [str(e)]},
            }
            return Response(response_error, status=status.HTTP_400_BAD_REQUEST)



class ProfileViewEdit(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.user_type == 'seller':
            profile = user.seller_profile
            serializer = SellerProfileSerializer(profile)
        else:
            profile = user.customer_profile
            serializer = CustomerProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        if user.user_type == 'seller':
            serializer = SellerProfileSerializer(user.seller_profile, data=request.data, partial=True)
        else:
            serializer = CustomerProfileSerializer(user.customer_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully", "data": serializer.data})
        return Response(serializer.errors, status=400)




class ChangePassword(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def put(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        try:
            obj = request.user
            print(obj)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if not obj.check_password(old_password):
            return Response({"error": "Old password does not match"}, status=400)

        obj.set_password(new_password)
        obj.save()
        return Response({"success": "Password changed successfully"}, status=200)




class PasswordResetRequestAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"success": True, "message": "OTP sent to email."}, 
                status=status.HTTP_200_OK
            )
        return Response(
            {"success": False, "errors": serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )



class OTPVerificationAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"success": True, "message": "OTP verified successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )




class PasswordResetAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Password reset successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    




#Google login view
class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)

            user = self.user  # Set by SocialLoginView
            if not user.user_type:
                user_type = request.data.get("user_type")
                if user_type not in ['seller', 'customer']:
                    return Response({"error": "user_type is required (seller/customer)"}, status=status.HTTP_400_BAD_REQUEST)
                user.user_type = user_type
                user.save()

                # Create default profile
                if user_type == "customer" and not hasattr(user, 'customer_profile'):
                    CustomerProfile.objects.create(user=user, first_name="", last_name="", mobile_number="")
                elif user_type == "seller" and not hasattr(user, 'seller_profile'):
                    SellerProfile.objects.create(user=user, name="", mobile_number="")

            
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    # "name": user.name,
                    "user_type": user.user_type,
                }
            })
        
        except OAuth2Error as e:
            return Response({
                "error": "Access token expired or invalid. Please login again.",
                "detail": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)




#Google Login with Serializer
# class GoogleLoginView(SocialLoginView):
#     adapter_class = GoogleOAuth2Adapter
#     serializer_class = CustomGoogleLoginSerializer  # your custom serializer

#     def post(self, request, *args, **kwargs):
#         try:
#             # Call parent post logic (token validation + login)
#             super_response = super().post(request, *args, **kwargs)

#             user = self.serializer.validated_data.get('user') or getattr(self.serializer, 'user', None)
#             if not user:
#                 return Response({"detail": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 "access": str(refresh.access_token),
#                 "refresh": str(refresh),
#                 "user": {
#                     "id": user.id,
#                     "email": user.email,
#                     "user_type": user.user_type,
#                     # Add other fields if needed
#                 }
#             })
        
#         except OAuth2Error as e:
#             return Response({
#                 "error": "Access token expired or invalid. Please login again.",
#                 "detail": str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)




#Apple Login View
class AppleLoginView(SocialLoginView):
    adapter_class = AppleOAuth2Adapter

    def post(self, request, *args, **kwargs):
        try:
            if not request.data.get("id_token"):
                return Response({"error": "id_token is required"}, status=400)
            return super().post(request, *args, **kwargs)
            response = super().post(request, *args, **kwargs)
            user = self.user
            print(user)

        except OAuth2Error as e:
            return Response({
                "error": "Access token expired or invalid. Please login again.",
                "detail": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        





# Mobile OTP Request View
class MobileOTPRequestAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = MobileOTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.context['user']
            user.generate_otp()

            print(user.otp)

            return Response(
                {"success": True, "message": "OTP sent to mobile number."},
                status=status.HTTP_200_OK
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )



# Mobile OTP Request View with API Key
# class MobileOTPRequestAPIView(APIView):
#     permission_classes = []

#     def post(self, request):
#         serializer = MobileOTPRequestSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.context['user']
#             sms_response = user.generate_otp()

#             if sms_response and sms_response.get("response_code") == "SUCCESS":
#                 return Response(
#                     {"success": True, "message": "OTP sent to mobile number."},
#                     status=status.HTTP_200_OK
#                 )
#             else:
#                 return Response(
#                     {"success": False, "message": "Failed to send OTP. Please check number or API key."},
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                 )

#         return Response(
#             {"success": False, "errors": serializer.errors},
#             status=status.HTTP_400_BAD_REQUEST
#         )




class MobileOTPVerificationAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = MobileOTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"success": True, "message": "OTP verified successfully."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class MobilePasswordResetAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = MobilePasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Password reset successfully."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )



# Contact Option Check API View
class ContactOptionCheckAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ContactOptionCheckSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
