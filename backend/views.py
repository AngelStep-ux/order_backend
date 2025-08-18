from django.http import HttpResponse
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import permissions
from django.contrib.auth import get_user_model
from rest_framework.views import APIView

User = get_user_model()

from .models import (
    Product,
    Category,
    Shop,
    Order,
    OrderItem,
    ProductInfo,
    Contact,
)
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    ShopSerializer,
    OrderSerializer,
    OrderItemSerializer,
    UserSerializer,
    ContactSerializer,
)

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken


def initial_page(request):
    return HttpResponse('Welcome to the web service for ordering goods!')


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductInfoListView(generics.ListAPIView):
    queryset = ProductInfo.objects.select_related('product', 'shop').all()
    serializer_class = ProductSerializer


class ContactListCreateView(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)


class ContactDestroyView(generics.DestroyAPIView):
    queryset = Contact.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class UserOrdersListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-dt')


class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        items_data = request.data.get('items')
        if not items_data:
            return Response({"error": "Нет данных"}, status=400)

        order = Order.objects.create(user=request.user, status='new')

        for item in items_data:
            product_info_id = item.get('product_info_id')
            quantity = item.get('quantity', 1)
            try:
                product_info = ProductInfo.objects.get(id=product_info_id)
                shop = product_info.shop
                OrderItem.objects.create(
                    order=order,
                    product_info=product_info,
                    shop=shop,
                    quantity=quantity
                )
            except ProductInfo.DoesNotExist:
                return Response({"error": f"Товар с id {product_info_id} не найден"}, status=404)

        serializer = OrderSerializer(order)
        return Response(serializer.data)


# Вьюха для импорта товаров
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


# Вьюха для получения списка товаров
@api_view(['GET'])
def get_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


class ExportProductsView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

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