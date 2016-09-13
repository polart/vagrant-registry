from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=User,
          dispatch_uid='create_auth_token')
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=User,
          dispatch_uid='create_user_profile')
def create_user_profile(sender, instance=None, created=False, **kwargs):
    if created:
        from .models import UserProfile
        UserProfile.objects.create(user=instance)
