from celery import shared_task
from easy_thumbnails.files import get_thumbnailer

@shared_task
def generate_avatar_thumbnails(image_path):
    thumbnailer = get_thumbnailer(image_path)
    thumbnailer.get_thumbnail({'size': (100, 100), 'crop': True})

@shared_task
def generate_product_thumbnails(image_path):
    thumbnailer = get_thumbnailer(image_path)
    thumbnailer.get_thumbnail({'size': (300, 300), 'crop': True})