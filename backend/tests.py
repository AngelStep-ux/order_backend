from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
import base64

from .models import Shop, Category, Product, ProductInfo, Contact, Order

User = get_user_model()

class Tests(APITestCase):

    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(username='testuser', password='testpass', email='test@test.com')
        self.client.login(username='testuser', password='testpass')

        # Создаем магазины
        self.shop1 = Shop.objects.create(name='Shop1', url='http://shop1.com')
        self.shop2 = Shop.objects.create(name='Shop2', url='http://shop2.com')

        # Создаем категорию и связываем с магазинами
        self.category = Category.objects.create(name='Category1')
        self.category.shops.set([self.shop1, self.shop2])

        # Создаем товар и связанный ProductInfo
        self.product = Product.objects.create(name='Товар1', description='Описание', price=100)
        self.product_info = ProductInfo.objects.create(
            product=self.product,
            shop=self.shop1,
            name='Инфо1',
            quantity=10,
            price=100,
            price_rrc=150
        )

        # Создаем контакт
        self.contact = Contact.objects.create(type='phone', user=self.user, value='123456789')

        # Создаем заказ
        self.order = Order.objects.create(user=self.user, status='pending')

    def test_initial_page(self):
        url = reverse('initial_page')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_send_order_confirmation(self):
        url = reverse('send_order_confirmation', args=[self.order.id])
        data = {'address': 'Test Address'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_confirm_order_by_link(self):
        # Кодируем order.id в URL-safe base64
        order_id_str = str(self.order.id)
        order_id_bytes = order_id_str.encode('utf-8')
        uidb64 = base64.urlsafe_b64encode(order_id_bytes).decode('utf-8')

        url = reverse('confirm_order', args=[uidb64])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Заказ подтвержден!')

    def test_get_cart(self):
        url = reverse('get_cart')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_product_to_cart(self):
        url = reverse('add_product')
        data = {'id': self.product_info.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_order(self):
        url = reverse('create_order')
        data = {
            'name': 'Test User',
            'phone': '123456789',
            'address': 'Test Address'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)