import os
import django
import yaml

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')
django.setup()

from backend.models import Shop, Category, Product, ProductInfo

yaml_path = "/home/admin1/Рабочий стол/my_project/backend/shop1.yaml"

with open(yaml_path, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

shop_name = data.get('shop')
if not shop_name:
    print("Не найдено название магазина ('shop') в YAML.")
    exit(1)

shop_obj, _ = Shop.objects.get_or_create(name=shop_name)

categories_data = data.get('categories', [])
category_map = {}
for cat in categories_data:
    category_obj, _ = Category.objects.get_or_create(name=cat['name'])
    category_map[cat['id']] = category_obj

goods = data.get('goods', [])
for item in goods:
    cat_id = item['category']
    category_obj = category_map.get(cat_id)
    if not category_obj:
        print(f"Категория с id {cat_id} не найдена для товара {item['name']}")
        continue

    product_obj, _ = Product.objects.update_or_create(
        name=item['name'],
        defaults={
            'description': '',
            'category': category_obj,
        }
    )

    ProductInfo.objects.update_or_create(
        product=product_obj,
        shop=shop_obj,
        defaults={
            'name': item['model'],
            'quantity': item['quantity'],
            'price': item['price'],
            'price_rrc': item.get('price_rrc'),
        }
    )

print("Импорт завершен.")