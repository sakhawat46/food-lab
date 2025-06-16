from django.urls import path,include
from . import views
urlpatterns = [
    path('test/',views.test, name='test'),
    path('products/create/', views.ProductCreateAPIView.as_view(), name='product-create'),
    path('products/', views.ProductListAPIView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='product-detail'),

]

