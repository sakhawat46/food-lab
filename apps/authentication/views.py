from django.contrib.auth import authenticate
from .serializers import SignupSerializer, LoginSerializer, ChangePasswordSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import PasswordResetRequestSerializer, OTPVerificationSerializer, PasswordResetSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import RetrieveUpdateAPIView
from .models import SellerProfile, CustomerProfile
from .serializers import SellerProfileSerializer, CustomerProfileSerializer

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
    permission_classes = []

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
