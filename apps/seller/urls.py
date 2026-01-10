from django.urls import path
from .views import ShopAPIView, ShopImageAPIView, ShopDocumentAPIView, ShopMapAPIView, NearbyShopsAPIView, ShopSearchAPIView

urlpatterns = [
    path('shop/', ShopAPIView.as_view(), name='shop-crud'),
    path('shop/images/', ShopImageAPIView.as_view(), name='shop-image-upload'),
    path('shop/documents/', ShopDocumentAPIView.as_view(), name='shop-documents'),
    path('shop/map/', ShopMapAPIView.as_view(), name='shop-map'),
    path('shop/map/nearby/', NearbyShopsAPIView.as_view(), name='nearby-shops'),
    path("shop/search/", ShopSearchAPIView.as_view(), name="shop-search"),
]
