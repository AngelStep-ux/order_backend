from rest_framework import serializers
from .models import (
    Product,
    Category,
    Shop,
    Order,
    OrderItem,
    User,
    Contact,
    Cart,
    CartItem,
    ProductInfo
)

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
        model = Product
        fields = ['id', 'product', 'shop_name', 'name', 'quantity', 'price']

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model=Contact
        fields=['id','type','value']

class OrderItemSerializer(serializers.ModelSerializer):
    product_info = serializers.SerializerMethodField()
    shop_name = serializers.CharField(source='product_info.shop.name', read_only=True)

    class Meta:
        model=OrderItem
        fields=['id','product_info','shop_name','quantity']

    def get_product_info(self, obj):
        return {
            'id': obj.product_info.id,
            'name': obj.product_info.name,
            'product': {
                'id': obj.product_info.product.id,
                'name': obj.product_info.product.name,
            },
            'shop': obj.product_info.shop.name,
            'quantity': obj.product_info.quantity,
            'price': obj.product_info.price,
        }

class OrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True)
    user=serializers.StringRelatedField()

    class Meta:
        model=Order
        fields=['id','user','dt','status','items']

class UserSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=['id','username','email','password']

    def create(self, validated_data):
        user=User(
            username=validated_data['username'],
            email=validated_data.get('email'),
            is_active=False
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


