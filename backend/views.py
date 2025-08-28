from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import (
    Product,
    Category,
    Shop,
    Order,
    OrderItem,
    ProductInfo,
    Contact,
    Cart,
    CartItem
)
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    ShopSerializer,
    OrderSerializer,
    UserSerializer,
    ContactSerializer,
    CartSerializer,
)

User = get_user_model()

def initial_page(request):
    return HttpResponse('Welcome to the web service for ordering goods!')

def send_activation_email(request, user):
    current_site = get_current_site(request)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = f"http://{current_site.domain}{reverse('activate', args=[uidb64, token])}"

    subject = 'Подтверждение регистрации'
    message = f'Для подтверждения перейдите по ссылке: {activation_link}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        request = self.request
        send_activation_email(request, user)

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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        recipient_emails = [self.request.user.email] if self.request.user.is_authenticated and hasattr(
            self.request.user, 'email') else []

        products_info = serializer.validated_data.get('products_info', [])
        for item in products_info:
            product_info_id = item.get('product_info_id')
            quantity = item.get('quantity', 1)
            try:
                product_info = ProductInfo.objects.get(id=product_info_id)
                OrderItem.objects.create(order=order, product_info=product_info, quantity=quantity)
            except ProductInfo.DoesNotExist:
                continue

        send_mail(
            subject='Подтверждение заказа',
            message=f'Ваш заказ #{order.id} создан. Адрес доставки: {order.address}',
            from_email='alina.step@mail.ru',
            recipient_list=recipient_emails,
            fail_silently=False,
        )

class OrderConfirmUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        try:
            order = self.get_queryset().get(pk=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'detail': 'Заказ не найден.'}, status=status.HTTP_404_NOT_FOUND)

        if order.is_confirmed:
            return Response({'detail': 'Заказ уже подтвержден.'}, status=status.HTTP_400_BAD_REQUEST)

        order.is_confirmed = True
        order.confirmed_at = timezone.now()
        order.save()

        return Response({'detail': 'Заказ подтвержден.'})

class ListOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

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
    return Response({'error': 'Метод не разрешен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

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

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Ваш аккаунт активирован! Теперь вы можете войти.')
    else:
        return HttpResponse('Некорректная ссылка или срок действия истек.')

# Работа с корзиной
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request):
    product_info_id = request.data.get('product_info_id')
    quantity = int(request.data.get('quantity', 1))

    if not product_info_id:
        return Response({'error': 'Product info ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product_info = ProductInfo.objects.get(id=product_info_id)
    except ProductInfo.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_info=product_info,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return Response({'message': 'Товар добавлен в корзину'})

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
    except CartItem.DoesNotExist:
        return Response({'error': 'Элемент не найден'}, status=status.HTTP_404_NOT_FOUND)

    quantity = int(request.data.get('quantity'))
    if quantity <= 0:
        cart_item.delete()
        return Response({'message': 'Элемент удален из корзины'})

    cart_item.quantity = quantity
    cart_item.save()
    return Response({'message': 'Количество обновлено'})

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_cart(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        cart_item.delete()
        return Response({'message': 'Элемент удален'})
    except CartItem.DoesNotExist:
        return Response({'error': 'Элемент не найден'}, status=status.HTTP_404_NOT_FOUND)

class SendOrderConfirmationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=404)

        address = request.data.get('address')
        if not address:
            return Response({'error': 'Пожалуйста, укажите адрес доставки.'}, status=400)

        # статус "ожидает подтверждения"
        order.address = address
        order.status = 'pending_confirmation'
        order.save()

        # ссылка для подтверждения
        uidb64 = urlsafe_base64_encode(str(order.id).encode())
        confirm_url = f"http://{request.get_host()}{reverse('confirm_order', args=[uidb64])}"

        # отправляем письмо с ссылкой
        subject = 'Подтверждение заказа'
        message = f'Для подтверждения заказа перейдите по ссылке: {confirm_url}'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [request.user.email])

        return Response({'message': 'Письмо с подтверждением отправлено'})

class ConfirmOrderByLinkView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64):
        try:
            order_id_str = urlsafe_base64_decode(uidb64).decode()
            order_id = int(order_id_str)
            order = Order.objects.get(id=order_id)
        except (TypeError, ValueError, OverflowError, Order.DoesNotExist):
            return HttpResponse('Некорректная ссылка или заказ не найден.', status=404)

        # статус "ожидает подтверждения"
        if order.status != 'pending_confirmation':
            return HttpResponse('Этот заказ уже подтвержден или недоступен для подтверждения.', status=400)

        # подтверждаем заказ
        order.status = 'confirmed'
        order.confirmed_at = timezone.now()
        order.save()

        return HttpResponse('Заказ подтвержден! Спасибо за покупку.')

class OrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class UserOrdersPageView(TemplateView):
    template_name = 'user_orders.html'