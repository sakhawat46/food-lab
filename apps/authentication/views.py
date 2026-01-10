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


class BaseAPIView(APIView):
    def success_response(self, message="Your request Accepted", data=None, status_code= status.HTTP_200_OK):
        return Response(
            {
            "success": True,
            "message": message,
            "status": status_code,
            "data": data or {}
            },
            status=status_code )
    def error_response(self, message="Your request rejected", data=None, status_code= status.HTTP_400_BAD_REQUEST):
        return Response(
            {
            "success": False,
            "message": message,
            "status": status_code,
            "data": data or {}
            },
            status=status_code )  



class SignupView(BaseAPIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response("User created successfully.")
        return self.error_response("Validation error", data=serializer.errors)



class LoginView(BaseAPIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return self.success_response("Login successful", data=serializer.validated_data)
        return self.error_response("Invalid credentials", data=serializer.errors)





class LogoutView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return self.error_response("Refresh token is required")

            token = RefreshToken(refresh_token)
            token.blacklist()
            return self.success_response("Successfully logged out.", status_code=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return self.error_response("Logout failed", data={"error": [str(e)]})






class ProfileViewEdit(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.user_type == 'seller':
            serializer = SellerProfileSerializer(user.seller_profile)
        else:
            serializer = CustomerProfileSerializer(user.customer_profile)
        return self.success_response("Profile retrieved successfully", serializer.data)

    def put(self, request):
        user = request.user
        if user.user_type == 'seller':
            serializer = SellerProfileSerializer(user.seller_profile, data=request.data, partial=True)
        else:
            serializer = CustomerProfileSerializer(user.customer_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return self.success_response("Profile updated successfully", serializer.data)
        return self.error_response("Update failed", serializer.errors)





class ChangePassword(BaseAPIView, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def put(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return self.error_response("Validation error", data=serializer.errors)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            return self.error_response("Old password does not match")

        user.set_password(new_password)
        user.save()
        return self.success_response("Password changed successfully")





class PasswordResetRequestAPIView(BaseAPIView):
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            return self.success_response("OTP sent to email.")
        return self.error_response("Validation error", serializer.errors)




class OTPVerificationAPIView(BaseAPIView):
    permission_classes = []

    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            return self.success_response("OTP verified successfully.")
        return self.error_response("Invalid OTP", serializer.errors)





class PasswordResetAPIView(BaseAPIView):
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response("Password reset successfully.")
        return self.error_response("Reset failed", serializer.errors)

    




#Google login view
# class GoogleLoginView(SocialLoginView):
#     adapter_class = GoogleOAuth2Adapter

#     def post(self, request, *args, **kwargs):
#         try:
#             response = super().post(request, *args, **kwargs)

#             user = self.user  # Set by SocialLoginView
            
#             if not user.user_type:
#                 user_type = request.data.get("user_type")
#                 if user_type not in ['seller', 'customer']:
#                     return Response({
#                         "success": False,
#                         "message": "user_type is required (seller/customer)",
#                         "status": status.HTTP_400_BAD_REQUEST,
#                         "data": {}
#                     }, status=status.HTTP_400_BAD_REQUEST)

#                 user.user_type = user_type
#                 user.save()

#                 # Create default profile
#                 if user_type == "customer" and not hasattr(user, 'customer_profile'):
#                     CustomerProfile.objects.create(user=user, first_name="", last_name="", mobile_number="")
#                 elif user_type == "seller" and not hasattr(user, 'seller_profile'):
#                     SellerProfile.objects.create(user=user, name="", mobile_number="")

#             refresh = RefreshToken.for_user(user)

#             return Response({
#                 "success": True,
#                 "message": "Google login successful.",
#                 "status": status.HTTP_200_OK,
#                 "data": {
#                     "access": str(refresh.access_token),
#                     "refresh": str(refresh),
#                     "user": {
#                         "id": user.id,
#                         "email": user.email,
#                         "user_type": user.user_type,
#                     }
#                 }
#             }, status=status.HTTP_200_OK)

#         except OAuth2Error as e:
#             return Response({
#                 "success": False,
#                 "message": "Access token expired or invalid. Please login again.",
#                 "status": status.HTTP_400_BAD_REQUEST,
#                 "data": {"detail": str(e)}
#             }, status=status.HTTP_400_BAD_REQUEST)

class GoogleLoginView(BaseAPIView, SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            user = self.user  # Set by SocialLoginView

            if not user.user_type:
                user_type = request.data.get("user_type")
                if user_type not in ['seller', 'customer']:
                    return self.error_response(
                        message="user_type is required (seller/customer)",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                user.user_type = user_type
                user.save()

                # Create default profile
                if user_type == "customer" and not hasattr(user, 'customer_profile'):
                    CustomerProfile.objects.create(
                        user=user, first_name="", last_name="", mobile_number=""
                    )
                elif user_type == "seller" and not hasattr(user, 'seller_profile'):
                    SellerProfile.objects.create(
                        user=user, name="", mobile_number=""
                    )

            refresh = RefreshToken.for_user(user)

            return self.success_response(
                message="Google login successful.",
                data={
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "user_type": user.user_type,
                    }
                },
                status_code=status.HTTP_200_OK
            )

        except OAuth2Error as e:
            return self.error_response(
                message="Access token expired or invalid. Please login again.",
                data={"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST
            )







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
class AppleLoginView(BaseAPIView, SocialLoginView):
    adapter_class = AppleOAuth2Adapter

    def post(self, request, *args, **kwargs):
        try:
            id_token = request.data.get("id_token")
            if not id_token:
                return self.error_response(
                    message="id_token is required",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            response = super().post(request, *args, **kwargs)
            user = self.user

            return self.success_response(
                message="Apple login successful.",
                data={
                    "access": response.data.get("access_token"),
                    "refresh": response.data.get("refresh_token"),
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "user_type": user.user_type,
                    }
                },
                status_code=status.HTTP_200_OK
            )

        except OAuth2Error as e:
            return self.error_response(
                message="Access token expired or invalid. Please login again.",
                data={"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        





# Mobile OTP Request View
class MobileOTPRequestAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = MobileOTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.context['user']
            user.generate_otp()

            print(user.otp)  # Only for debugging; remove in production

            return Response({
                "success": True,
                "message": "OTP sent to mobile number.",
                "status": status.HTTP_200_OK,
                "data": {}
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "Validation failed.",
            "status": status.HTTP_400_BAD_REQUEST,
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



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




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class MobileOTPVerificationAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = MobileOTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                "success": True,
                "message": "OTP verified successfully.",
                "status": status.HTTP_200_OK,
                "data": {}
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "OTP verification failed.",
            "status": status.HTTP_400_BAD_REQUEST,
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class MobilePasswordResetAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = MobilePasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Password reset successfully.",
                "status": status.HTTP_200_OK,
                "data": {}
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "Password reset failed.",
            "status": status.HTTP_400_BAD_REQUEST,
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)




# Contact Option Check API View
class ContactOptionCheckAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ContactOptionCheckSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                "success": True,
                "message": "Contact option verified successfully.",
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "Validation failed.",
            "status": status.HTTP_400_BAD_REQUEST,
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)