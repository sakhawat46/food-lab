from django.urls import path, include
from .views import SignupView, LoginView, LogoutView, ProfileViewEdit
from rest_framework_simplejwt.views import TokenRefreshView
from .views import PasswordResetRequestAPIView, OTPVerificationAPIView, PasswordResetAPIView, ChangePassword

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path('profile/', ProfileViewEdit.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("change-password/", ChangePassword.as_view(), name="change_password"),
    path("password-reset/request/", PasswordResetRequestAPIView.as_view(), name="password-reset-request"),
    path("password-reset/verify-otp/", OTPVerificationAPIView.as_view(), name="password-reset-verify-otp"),
    path("password-reset/change-password/", PasswordResetAPIView.as_view(), name="password-reset-change"),

]
