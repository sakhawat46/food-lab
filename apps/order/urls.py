from django.urls import path
from .views import *

urlpatterns = [
    # Customer
    path('customer/orders/', CustomerOrderListAPIView.as_view()),
    path('customer/orders/create/', CustomerOrderCreateAPIView.as_view()),
    path('customer/orders/<int:order_id>/feedback/', OrderFeedbackSubmitAPIView.as_view()),

    # Seller
    path('seller/orders/', SellerOrderListAPIView.as_view()),
    path('seller/orders/<int:pk>/update/', SellerOrderUpdateView.as_view(), name='seller-order-update'),
    path('seller/orders/summary/',SellerOrderSummaryView.as_view(),name="seller_order_summary")

]
