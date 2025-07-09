from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.urls import path
from .models import Shop, ShopImage, ShopDocument
from .serializers import (
    ShopSerializer,
    ShopImageSerializer,
    ShopDocumentSerializer,
    ShopMapSerializer,
    ShopSearchSerializer
)
from apps.notification.utils import create_notification
from .utils import haversine_distance
from django.db.models import Q



class BaseAPIView(APIView):
    def success_response(self, message="Your request Accepted", data=None, status_code= status.HTTP_200_OK):
        return Response(
            {
            "success": True,
            "message": message,
            "status": status_code,
            "data": data or {}
            },
            status=status_code )
    def error_response(self, message="Your request rejected", data=None, status_code= status.HTTP_400_BAD_REQUEST):
        return Response(
            {
            "success": False,
            "message": message,
            "status": status_code,
            "data": data or {}
            },
            status=status_code )  



class ShopAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        shop = getattr(request.user, 'shop', None)
        if not shop:
            return self.error_response(
                message="Shop not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = ShopSerializer(shop)
        return self.success_response(
            message="Shop retrieved successfully.",
            data=serializer.data
        )

    def post(self, request):
        if request.user.user_type != 'seller':
            return self.error_response(
                message="Only sellers can create a shop.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        if hasattr(request.user, 'shop'):
            return self.error_response(
                message="You have already created a shop.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer = ShopSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            shop = serializer.save(owner=request.user)
            create_notification(
                request.user,
                "Store Created",
                "Your store has been created successfully."
            )
            return self.success_response(
                message="Shop created successfully.",
                data=ShopSerializer(shop).data,
                status_code=status.HTTP_201_CREATED
            )

        return self.error_response(
            message="Failed to create shop.",
            data=serializer.errors
        )

    def put(self, request):
        shop = get_object_or_404(Shop, owner=request.user)
        serializer = ShopSerializer(shop, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                message="Shop updated successfully.",
                data=serializer.data
            )
        return self.error_response(
            message="Failed to update shop.",
            data=serializer.errors
        )




from rest_framework.parsers import MultiPartParser, FormParser

class ShopImageAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        shop = get_object_or_404(Shop, owner=request.user)
        images = request.FILES.getlist('images')
        created_images = []
        for image in images:
            img_obj = ShopImage.objects.create(shop=shop, image=image)
            created_images.append(ShopImageSerializer(img_obj).data)
        return self.success_response(
            message="Images uploaded successfully.",
            data={"images": created_images},
            status_code=status.HTTP_201_CREATED
        )




class ShopDocumentAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        shop = get_object_or_404(Shop, owner=request.user)
        document = getattr(shop, 'documents', None)
        if not document:
            return self.error_response(
                message="Documents not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        serializer = ShopDocumentSerializer(document)
        return self.success_response(
            message="Shop documents retrieved successfully.",
            data=serializer.data
        )

    def post(self, request):
        shop = get_object_or_404(Shop, owner=request.user)
        data = request.data.copy()

        try:
            document = shop.documents
            serializer = ShopDocumentSerializer(document, data=data, partial=True)
        except ShopDocument.DoesNotExist:
            serializer = ShopDocumentSerializer(data=data)

        if serializer.is_valid():
            serializer.save(shop=shop)
            return self.success_response(
                message="Documents saved successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Failed to save documents.",
            data=serializer.errors
        )

    def put(self, request):
        shop = get_object_or_404(Shop, owner=request.user)
        document = get_object_or_404(ShopDocument, shop=shop)
        serializer = ShopDocumentSerializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                message="Documents updated successfully.",
                data=serializer.data
            )
        return self.error_response(
            message="Failed to update documents.",
            data=serializer.errors
        )

       



class ShopMapAPIView(BaseAPIView):

    def get(self, request):
        category_name = request.query_params.get('category')

        shops = Shop.objects.exclude(latitude__isnull=True, longitude__isnull=True).prefetch_related('categories')

        if category_name:
            shops = shops.filter(categories__name__iexact=category_name)

        serializer = ShopMapSerializer(shops, many=True)
        return self.success_response(
            message="Shops retrieved successfully.",
            data=serializer.data
        )




class NearbyShopsAPIView(BaseAPIView):

    def get(self, request):
        try:
            user_lat = float(request.query_params.get("lat"))
            user_lon = float(request.query_params.get("lon"))
        except (TypeError, ValueError):
            return self.error_response(
                message="Missing or invalid coordinates",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        radius = float(request.query_params.get("radius", 10))  # default 10 km

        shops = Shop.objects.exclude(latitude__isnull=True, longitude__isnull=True).prefetch_related('categories')
        nearby_shops = [
            shop for shop in shops
            if haversine_distance(user_lat, user_lon, float(shop.latitude), float(shop.longitude)) <= radius
        ]

        serializer = ShopMapSerializer(nearby_shops, many=True)
        return self.success_response(
            message="Nearby shops retrieved successfully.",
            data=serializer.data
        )

    



class ShopSearchAPIView(BaseAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        shops = Shop.objects.filter(shop_name__icontains=query).order_by('shop_name')[:10]
        serializer = ShopSearchSerializer(shops, many=True, context={'request': request})
        return self.success_response(
            message="Shops retrieved successfully.",
            data=serializer.data
        )
