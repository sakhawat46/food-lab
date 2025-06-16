from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from .models import Product
from .serializers import ProductSerializer

class ProductCreateView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)