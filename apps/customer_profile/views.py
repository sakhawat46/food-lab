from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Address
from .serializers import AddressSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated



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




class AddressListCreateAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return self.success_response(
            message="Addresses retrieved successfully.",
            data=serializer.data
        )

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return self.success_response(
                message="Address added successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Failed to add address.",
            data=serializer.errors
        )



class AddressDetailAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Address, pk=pk, user=user)

    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return self.success_response(
            message="Addresses retrieved successfully.",
            data=serializer.data
        )

    def put(self, request, pk):
        address = self.get_object(pk, request.user)
        serializer = AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return self.success_response(
                message="Address updated successfully.",
                data=serializer.data
            )
        return self.error_response(
            message="Failed to update address.",
            data=serializer.errors
        )

    def delete(self, request, pk):
        address = self.get_object(pk, request.user)
        address.delete()
        return self.success_response(
            message="Address deleted successfully.",
            data={},
            status_code=status.HTTP_204_NO_CONTENT
        )

