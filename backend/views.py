from rest_framework import viewsets
from .models import Product, Category, Shop, Order, OrderItem
from .serializers import ProductSerializer, CategorySerializer, ShopSerializer, OrderSerializer, OrderItemSerializer

def intial_page(request):
    return HttpResponse('Welcome to the web service for ordering goods!')

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
