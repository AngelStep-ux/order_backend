from django.http import HttpResponse
from rest_framework import viewsets
from .models import Product, Category, Shop, Order, OrderItem, ProductInfo
from .serializers import ProductSerializer, CategorySerializer, ShopSerializer, OrderSerializer, OrderItemSerializer
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
import json

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView

def intial_page(request):
    return HttpResponse('Welcome to the web service for ordering goods!')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


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
    serializer_class = OrderItemSerializer

class ExportProductsView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        products = self.get_queryset()
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)



@api_view(['POST'])
def import_products(request):
    if request.method == 'POST':
        data = request.data
        for item in data.get('goods', []):
            category_id = item['category']
            category_name_map = {
                224: 'Смартфоны',
                15: 'Аксессуары',
                1: 'Flash-накопители',
                5: 'Телевизоры'
            }
            category_name = category_name_map.get(category_id, f'Категория {category_id}')
            category, created = Category.objects.get_or_create(name=category_name)

            product_name = item['name']
            description = ''
            price = item['price']

            product, created = Product.objects.get_or_create(
                name=product_name,
                defaults={'category': category, 'description': description}
            )

            shop_name = data.get('shop', 'Default Shop')
            shop, _ = Shop.objects.get_or_create(name=shop_name)

            ProductInfo.objects.update_or_create(
                product=product,
                shop=shop,
                defaults={
                    'name': product_name,
                    'quantity': item.get('quantity', 0),
                    'price': price,
                    'price_rrc': item.get('price_rrc', price)
                }
            )

        return Response({'status': 'Импорт завершен'}, status=status.HTTP_201_CREATED)
    return Response({'error': 'Неверный метод'}, status=status.HTTP_400_BAD_REQUEST)
