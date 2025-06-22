from django.urls import path
from .views import AddressListCreateAPIView, AddressDetailAPIView

urlpatterns = [
    path('addresses/', AddressListCreateAPIView.as_view(), name='address-list-create'),
    path('addresses/<int:pk>/', AddressDetailAPIView.as_view(), name='address-detail'),
]
