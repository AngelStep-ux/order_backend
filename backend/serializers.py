from rest_framework import serializers
from .models import (
    Product,
    Category,
    Shop,
    User,
    Contact,
    Cart,
    CartItem,
    ProductInfo,
    Order,
    OrderItem
)


# сериализаторы для отображения и работы с данными

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)

    class Meta:
        model = ProductInfo
        fields = ['id', 'product', 'shop_name', 'name', 'quantity', 'price']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'type', 'value']
        read_only_fields = ['user']


# СЕРИАЛИЗАТОРЫ ДЛЯ ЗАКАЗОВ

# для отображения элементов заказа с полной информацией о товаре и магазине
class OrderItemDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    shop_name = serializers.CharField(source='product.shop.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'shop_name', 'quantity']


# основной сериализатор заказа (для чтения)
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemDetailSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'address', 'items', 'is_confirmed', 'created_at']


# для создания заказа с вложенными элементами
class OrderCreateItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField()

    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity']

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        try:
            product = ProductInfo.objects.get(id=product_id)
        except ProductInfo.DoesNotExist:
            raise serializers.ValidationError("ProductInfo with given ID does not exist.")
        return OrderItem.objects.create(product=product, **validated_data)


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderCreateItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['user', 'address', 'status', 'is_confirmed', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            serializer = OrderCreateItemSerializer(data=item_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(order=order)
        return order


# другие сериализаторы

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email'),
            is_active=False
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CartItemSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product_info', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'items']


class OrderConfirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'address', 'status', 'is_confirmed']


class OrderUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status', 'is_confirmed']