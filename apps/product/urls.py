from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('test/',views.test, name='test'),
    path('products/create/', views.ProductCreateAPIView.as_view(), name='product-create'),
    path('products/', views.ProductListAPIView.as_view(), name='product-list'),
    path('products/search/', views.ProductSearchAPIView.as_view(), name='product-search'),
    path('products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='product-detail'),
    path('products/<int:product_id>/review/', views.ProductReviewCreateAPIView.as_view(), name='create-review'),
    path('reviews/<int:review_id>/reply/', views.SellerReplyReviewAPIView.as_view(), name='reply-review'),
    path('products/<int:product_id>/reviewss/', views.ProductReviewListAPIView.as_view()),
    path('reviews/<int:review_id>/report/', views.ReportReviewAPIView.as_view()),
    path('orders/create/', views.OrderCreateAPIView.as_view(), name='create-order'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

