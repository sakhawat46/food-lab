from django.urls import path
from .views import (
    CartListView,
    CartItemAddUpdateView,
    CartItemIncreaseView,
    CartItemDecreaseView,
    CartItemDeleteView,
    CheckoutView,
)

urlpatterns = [
    path('list/', CartListView.as_view(), name='cart-list'),
    path('add/', CartItemAddUpdateView.as_view(), name='cart-add-update'),
    path('increase/<int:pk>/', CartItemIncreaseView.as_view(), name='cart-increase'),
    path('decrease/<int:pk>/', CartItemDecreaseView.as_view(), name='cart-decrease'),
    path('delete/<int:pk>/', CartItemDeleteView.as_view(), name='cart-delete'),
    path('checkout/', CheckoutView.as_view(), name='cart-checkout'),
]
