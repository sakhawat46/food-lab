from django.urls import path
from .views import CompanyDetailsAPIView, BankDetailsAPIView, ContactRequestAPIView, AccountDeleteAPIView

urlpatterns = [
    path('company/details/', CompanyDetailsAPIView.as_view(), name='company-details'),
    path('bank/details/', BankDetailsAPIView.as_view(), name='bank-details'),
    path('contact/request/', ContactRequestAPIView.as_view(), name='contact-request'),
    path('account/delete/', AccountDeleteAPIView.as_view(), name='account-delete'),
]
