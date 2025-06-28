from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from apps.authentication.views import GoogleLoginView, AppleLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.authentication.urls')),
    path('api/v1/',include('apps.product.urls')),
    path('api/v1/',include('apps.order.urls')),
    path('api/v1/',include('apps.cart.urls')),

    path('api/v1/', include('apps.seller.urls')),
    path('api/v1/', include('apps.seller_profile.urls')),
    path('api/v1/', include('apps.chatting.urls')),
    path('api/v1/', include('apps.crave.urls')),
    path('api/v1/', include('apps.notification.urls')),
    path('api/v1/', include('apps.customer_profile.urls')),
    path('api/v1/', include('apps.dashboard.urls')),

    #Google login
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('auth/apple/', AppleLoginView.as_view(), name='apple_login'),

]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
