from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

STATUS_ORDERS = [
    ('new', 'Новый'),
    ('processing', 'Обрабатывается'),
    ('shipped', 'Отправлен'),
    ('completed', 'Завершен'),
    ('cancelled', 'Отменен'),
]

CONTACT_INFO = [
    ('phone', 'Телефон'),
    ('email', 'Email'),
    ('address', 'Адрес'),
]

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("Имя пользователя должно быть установлено")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    objects = UserManager()

class Shop(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"

class Category(models.Model):
    shops = models.ManyToManyField(Shop, help_text="Выберите магазин")
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

class ProductInfo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_infos')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='product_infos')
    name = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_rrc = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} {self.shop.name}"

    class Meta:
        verbose_name = "Информация о товаре"
        verbose_name_plural = "Информация о товарах"

class Parameter(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Параметр"
        verbose_name_plural = "Параметры"

class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='parameters')
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.parameter.name}: {self.value}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_ORDERS, default='new')

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(ProductInfo, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.shop.name}) in Order #{self.order.id}"

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"

class Contact(models.Model):
    type = models.CharField(max_length=30, choices=CONTACT_INFO)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.get_type_display()}: {self.value} ({self.user.username})"