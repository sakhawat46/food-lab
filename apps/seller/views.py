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



class ShopAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        shop = getattr(request.user, 'shop', None)
        if not shop:
            return Response({"detail": "Shop not found."}, status=404)

        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    def post(self, request):
        print("DEBUG: User =>", request.user.email, "Type =>", request.user.user_type)

        if request.user.user_type != 'seller':
            return Response({"error": "Only sellers can create a shop."}, status=403)

        if hasattr(request.user, 'shop'):
            return Response({"error": "You have already created a shop."}, status=400)

        serializer = ShopSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            shop = serializer.save(owner=request.user)
            create_notification(
                request.user,
                "Store Created",
                "Your store has been created successfully."
            )
            return Response(ShopSerializer(shop).data, status=201)

        return Response(serializer.errors, status=400)

    def put(self, request):
        shop = get_object_or_404(Shop, owner=request.user)
        serializer = ShopSerializer(shop, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)



class ShopImageAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        shop = get_object_or_404(Shop, owner=request.user)
        images = request.FILES.getlist('images')
        created_images = []
        for image in images:
            img_obj = ShopImage.objects.create(shop=shop, image=image)
            created_images.append(ShopImageSerializer(img_obj).data)
        return Response({"images": created_images}, status=201)


class ShopDocumentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        shop = get_object_or_404(Shop, owner=request.user)
        document = getattr(shop, 'documents', None)
        if not document:
            return Response({"detail": "Documents not found."}, status=404)
        serializer = ShopDocumentSerializer(document)
        return Response(serializer.data)


    def post(self, request):
        shop = get_object_or_404(Shop, owner=request.user)
        data = request.data.copy()

        try:
            # Try to get existing document for this shop
            document = shop.documents
            serializer = ShopDocumentSerializer(document, data=data, partial=True)
        except ShopDocument.DoesNotExist:
            # If no document exists, create a new one
            serializer = ShopDocumentSerializer(data=data)

        if serializer.is_valid():
            serializer.save(shop=shop)
            return Response({
                "message": "Documents saved successfully",
                "data": serializer.data
            }, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request):
        shop = get_object_or_404(Shop, owner=request.user)
        document = get_object_or_404(ShopDocument, shop=shop)
        serializer = ShopDocumentSerializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
       



class ShopMapAPIView(APIView):
    def get(self, request):
        category_name = request.query_params.get('category')

        shops = Shop.objects.exclude(latitude__isnull=True, longitude__isnull=True).prefetch_related('categories')

        if category_name:
            shops = shops.filter(categories__name__iexact=category_name)

        serializer = ShopMapSerializer(shops, many=True)
        return Response(serializer.data)



class NearbyShopsAPIView(APIView):
    def get(self, request):
        try:
            user_lat = float(request.query_params.get("lat"))
            user_lon = float(request.query_params.get("lon"))
        except (TypeError, ValueError):
            return Response({"error": "Missing or invalid coordinates"}, status=400)

        radius = float(request.query_params.get("radius", 10))  # default 10 km

        nearby_shops = []
        shops = Shop.objects.exclude(latitude__isnull=True, longitude__isnull=True).prefetch_related('categories')

        for shop in shops:
            dist = haversine_distance(user_lat, user_lon, float(shop.latitude), float(shop.longitude))
            if dist <= radius:
                nearby_shops.append(shop)

        serializer = ShopMapSerializer(nearby_shops, many=True)
        return Response(serializer.data)
    



class ShopSearchAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        shops = Shop.objects.filter(shop_name__icontains=query).order_by('shop_name')[:10]
        serializer = ShopSearchSerializer(shops, many=True, context={'request': request})
        return Response(serializer.data)