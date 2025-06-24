from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Product,ProductReview
from .serializers import ProductSerializer,ProductReviewSerializerwithReply
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
User=get_user_model()
def test(request):
    return HttpResponse("Hello, this is a test view from the product app.")

class IsSellerOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.seller == request.user

class ProductCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ProductListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        products = Product.objects.filter(seller=request.user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ProductDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSellerOwnerOrReadOnly]

    def get_object(self, pk, user):
        product = get_object_or_404(Product, pk=pk)
        self.check_object_permissions(self.request, product)
        return product

    def get(self, request, pk):
        product = self.get_object(pk, request.user)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = self.get_object(pk, request.user)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)  # Ensure seller is not changed
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk, request.user)
        product.delete()
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

class ProductSearchAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({"detail": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        products = Product.objects.filter(name__icontains=query, seller=request.user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)   
       
class ProductReviewCreateAPIView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,product_id):
        product=get_object_or_404(Product,id=product_id)
        if ProductReview.objects.filter(product=product, user=request.user).exists():
            return Response(
                {"detail": "You have already reviewed this product."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer=ProductReviewSerializerwithReply(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user,product=product)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

from django.utils import timezone

class SellerReplyReviewAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, review_id):
        review = get_object_or_404(ProductReview, id=review_id)

        # ✅ Ensure only the seller can reply
        if review.product.seller != request.user:
            return Response({"detail": "Only the seller can reply to this review."}, status=status.HTTP_403_FORBIDDEN)

        reply_text = request.data.get('seller_reply')
        if not reply_text:
            return Response({"detail": "Missing 'seller_reply'."}, status=status.HTTP_400_BAD_REQUEST)

        review.seller_reply = reply_text
        review.replyed_at = timezone.now()
        review.save()

        return Response({"message": "Reply added successfully."}, status=status.HTTP_200_OK)


     


class ProductReviewListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        product = Product.objects.get(id=product_id)
        reviews = product.reviews.all()
        serializer = ProductReviewSerializerwithReply(reviews, many=True)

        stats = product.reviews.aggregate(
            average_rating=Avg('rating'),
            total_reviews=Count('id')
        )

        return Response({
            "reviews": serializer.data,
            "average_rating": stats["average_rating"],
            "total_reviews": stats["total_reviews"]
        })
    
class ReportReviewAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, review_id):
        review = get_object_or_404(ProductReview, id=review_id)

        if review.product.seller != request.user:
            return Response({"detail": "Only the seller can report this review."}, status=status.HTTP_403_FORBIDDEN)

        reason = request.data.get('report_reason')
        valid_reasons = dict(ProductReview.REPORT_REASONS).keys()

        if reason not in valid_reasons:
            return Response({
                "detail": "Invalid report reason.",
                "valid_choices": ProductReview.REPORT_REASONS
            }, status=status.HTTP_400_BAD_REQUEST)

        review.is_reported = True
        review.report_reason = reason
        review.save()

        return Response({"message": "Review reported successfully."})



