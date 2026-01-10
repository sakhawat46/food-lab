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
class BaseAPIView(APIView):
    def success_response(self, message="Your request Accepted", data=None, status_code=status.HTTP_200_OK):
        return Response({
            "success": True,
            "message": message,
            "status": status_code,
            "data": data or {}
        }, status=status_code)

    def error_response(self, message="Your request rejected", data=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            "success": False,
            "message": message,
            "status": status_code,
            "data": data or {}
        }, status=status_code)
class ProductCreateAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                message="Product created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )

        return self.error_response(
            message="Product creation failed",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class ProductListAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return self.success_response(
            message="Products fetched successfully",
            data={"products": serializer.data}
        )
class ProductListOfSellerAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        products = Product.objects.filter(seller=request.user)
        serializer = ProductSerializer(products, many=True)
        return self.success_response(
            message="Products fetched successfully",
            data={"products": serializer.data}
        )

class ProductDetailAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated, IsSellerOwnerOrReadOnly]

    def get_object(self, pk, user):
        product = get_object_or_404(Product, pk=pk)
        self.check_object_permissions(self.request, product)
        return product

    def get(self, request, pk):
        product = self.get_object(pk, request.user)
        serializer = ProductSerializer(product)
        return self.success_response(
            message="Product retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        product = self.get_object(pk, request.user)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)  # Prevent changing seller
            return self.success_response(
                message="Product updated successfully",
                data=serializer.data
            )
        return self.error_response(
            message="Product update failed",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        product = self.get_object(pk, request.user)
        product.delete()
        return self.success_response(
            message="Product deleted successfully",
            data={},
            status_code=status.HTTP_204_NO_CONTENT
        )

    
class ProductSearchAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return self.error_response(
                message="Query parameter 'q' is required.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        products = Product.objects.filter(name__icontains=query, seller=request.user)
        serializer = ProductSerializer(products, many=True)
        return self.success_response(
            message=f"Found {len(products)} product(s) matching '{query}'.",
            data={"products": serializer.data}
        )

       
class ProductReviewCreateAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        if ProductReview.objects.filter(product=product, user=request.user).exists():
            return self.error_response(
                message="You have already reviewed this product.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer = ProductReviewSerializerwithReply(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return self.success_response(
                message="Review created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Review creation failed",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


from django.utils import timezone

class SellerReplyReviewAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, review_id):
        review = get_object_or_404(ProductReview, id=review_id)

        if review.product.seller != request.user:
            return self.error_response(
                message="Only the seller can reply to this review.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        reply_text = request.data.get('seller_reply')
        if not reply_text:
            return self.error_response(
                message="Missing 'seller_reply'.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        review.seller_reply = reply_text
        review.replyed_at = timezone.now()
        review.save()

        return self.success_response(
            message="Reply added successfully."
        )



     


class ProductReviewListAPIView(BaseAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return self.error_response(
                message="Product not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        reviews = product.reviews.all()
        serializer = ProductReviewSerializerwithReply(reviews, many=True)

        stats = product.reviews.aggregate(
            average_rating=Avg('rating'),
            total_reviews=Count('id')
        )

        return self.success_response(
            message="Reviews fetched successfully",
            data={
                "reviews": serializer.data,
                "average_rating": stats["average_rating"],
                "total_reviews": stats["total_reviews"]
            }
        )

class ReportReviewAPIView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, review_id):
        review = get_object_or_404(ProductReview, id=review_id)

        if review.product.seller != request.user:
            return self.error_response(
                message="Only the seller can report this review.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        reason = request.data.get('report_reason')
        valid_reasons = dict(ProductReview.REPORT_REASONS).keys()

        if reason not in valid_reasons:
            return self.error_response(
                message="Invalid report reason.",
                data={"valid_choices": ProductReview.REPORT_REASONS},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        review.is_reported = True
        review.report_reason = reason
        review.save()

        return self.success_response(
            message="Review reported successfully."
        )




