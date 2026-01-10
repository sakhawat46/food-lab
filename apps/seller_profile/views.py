from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import CompanyDetails, BankDetails, ContactRequest
from .serializers import CompanyDetailsSerializer, BankDetailsSerializer, ContactRequestSerializer



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



class CompanyDetailsAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            company = request.user.company_details
            serializer = CompanyDetailsSerializer(company)
            return self.success_response(
                message="Company details retrieved successfully.",
                data=serializer.data
            )
        except CompanyDetails.DoesNotExist:
            return self.error_response(
                message="Company details not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

    def post(self, request):
        if hasattr(request.user, 'company_details'):
            return self.error_response(
                message="Company details already exist.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer = CompanyDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_profile=request.user)
            return self.success_response(
                message="Company details created successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Failed to create company details.",
            data=serializer.errors
        )

    def put(self, request):
        try:
            company = request.user.company_details
        except CompanyDetails.DoesNotExist:
            return self.error_response(
                message="Company details not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = CompanyDetailsSerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                message="Company details updated successfully.",
                data=serializer.data
            )
        return self.error_response(
            message="Failed to update company details.",
            data=serializer.errors
        )





class BankDetailsAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            bank = request.user.bankdetails
            serializer = BankDetailsSerializer(bank)
            return self.success_response(
                message="Bank details retrieved successfully.",
                data=serializer.data
            )
        except BankDetails.DoesNotExist:
            return self.error_response(
                message="Bank details not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

    def post(self, request):
        if hasattr(request.user, 'bankdetails'):
            return self.error_response(
                message="Bank details already exist.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer = BankDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return self.success_response(
                message="Bank details created successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Failed to create bank details.",
            data=serializer.errors
        )

    def put(self, request):
        try:
            bank = request.user.bankdetails
        except BankDetails.DoesNotExist:
            return self.error_response(
                message="Bank details not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = BankDetailsSerializer(bank, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                message="Bank details updated successfully.",
                data=serializer.data
            )
        return self.error_response(
            message="Failed to update bank details.",
            data=serializer.errors
        )

    def delete(self, request):
        try:
            bank = request.user.bankdetails
            bank.delete()
            return self.success_response(
                message="Bank details deleted successfully.",
                data={},
                status_code=status.HTTP_204_NO_CONTENT
            )
        except BankDetails.DoesNotExist:
            return self.error_response(
                message="Bank details not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )




class ContactRequestAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ContactRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return self.success_response(
                message="Contact request submitted successfully.",
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Failed to submit contact request.",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


    


class AccountDeleteAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        email = user.email
        user.delete()
        return self.success_response(
            message=f"Account '{email}' has been permanently deleted.",
            status_code=status.HTTP_200_OK
        )