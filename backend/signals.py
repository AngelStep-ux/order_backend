from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Product
from .tasks import generate_avatar_thumbnails, generate_product_thumbnails

@receiver(post_save, sender=User)
def user_avatar_post_save(sender, instance, **kwargs):
    if instance.avatar:
        generate_avatar_thumbnails.delay(instance.avatar.path)

@receiver(post_save, sender=Product)
def product_image_post_save(sender, instance, **kwargs):
    if instance.image:
        generate_product_thumbnails.delay(instance.image.path)