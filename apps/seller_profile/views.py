from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import CompanyDetails, BankDetails, ContactRequest
from .serializers import CompanyDetailsSerializer, BankDetailsSerializer, ContactRequestSerializer

class CompanyDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            company = request.user.company_details
            serializer = CompanyDetailsSerializer(company)
            return Response(serializer.data)
        except CompanyDetails.DoesNotExist:
            return Response({"detail": "Company details not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if hasattr(request.user, 'company_details'):
            return Response({"detail": "Company details already exist."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CompanyDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_profile=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            company = request.user.company_details
        except CompanyDetails.DoesNotExist:
            return Response({"detail": "Company details not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompanyDetailsSerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Company details updated successfully", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class BankDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            bank = request.user.bankdetails
            serializer = BankDetailsSerializer(bank)
            return Response(serializer.data)
        except BankDetails.DoesNotExist:
            return Response({"detail": "Bank details not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if hasattr(request.user, 'bankdetails'):
            return Response({"detail": "Bank details already exist."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BankDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            bank = request.user.bankdetails
        except BankDetails.DoesNotExist:
            return Response({"detail": "Bank details not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BankDetailsSerializer(bank, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Bank details updated successfully", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            bank = request.user.bankdetails
            bank.delete()
            return Response({"message": "Bank details deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except BankDetails.DoesNotExist:
            return Response({"detail": "Bank details not found."}, status=status.HTTP_404_NOT_FOUND)



class ContactRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ContactRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Contact request submitted successfully."}, status=201)
        return Response(serializer.errors, status=400)

    


class AccountDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        email = user.email
        user.delete()
        return Response(
            {"message": f"Account '{email}' has been permanently deleted."},
            status=status.HTTP_200_OK
        )