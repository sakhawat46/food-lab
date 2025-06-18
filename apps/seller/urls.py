from django.urls import path
from .views import ShopAPIView, ShopImageAPIView, ShopDocumentAPIView

urlpatterns = [
    path('shop/', ShopAPIView.as_view(), name='shop-crud'),
    path('shop/images/', ShopImageAPIView.as_view(), name='shop-image-upload'),
    path('shop/documents/', ShopDocumentAPIView.as_view(), name='shop-documents'),
]
