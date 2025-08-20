import yaml
from django.core.management.base import BaseCommand
from backend.models import Product, Category, ProductInfo, Shop

class Command(BaseCommand):
    help = 'Импорт товаров из YAML'

    def handle(self, *args, **kwargs):
        path = '/home/admin1/Рабочий стол/my_project/shop1.yaml'
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        for item in data['goods']:
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

        self.stdout.write(self.style.SUCCESS('Импорт завершен'))