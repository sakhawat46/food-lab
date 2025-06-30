from django.urls import path, include
from .views import SignupView, LoginView, LogoutView, ProfileViewEdit
from rest_framework_simplejwt.views import TokenRefreshView
from .views import PasswordResetRequestAPIView, OTPVerificationAPIView, PasswordResetAPIView, ChangePassword, MobileOTPRequestAPIView, MobileOTPVerificationAPIView, MobilePasswordResetAPIView, ContactOptionCheckAPIView

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path('profile/', ProfileViewEdit.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("change-password/", ChangePassword.as_view(), name="change_password"),

    # Email OTP Request
    path("password-reset/request/", PasswordResetRequestAPIView.as_view(), name="password-reset-request"),
    path("password-reset/verify-otp/", OTPVerificationAPIView.as_view(), name="password-reset-verify-otp"),
    path("password-reset/change-password/", PasswordResetAPIView.as_view(), name="password-reset-change"),

    # Mobile OTP Request
    path('otp/send-mobile/', MobileOTPRequestAPIView.as_view(), name='send-otp-mobile'),
    path("otp/verify-mobile/", MobileOTPVerificationAPIView.as_view(), name="verify-otp-mobile"),
    path("otp/reset-mobile/", MobilePasswordResetAPIView.as_view(), name="reset-password-mobile"),

    # Contact Option Check
    path("otp/check-contact/", ContactOptionCheckAPIView.as_view(), name="check-contact-options"),

]
