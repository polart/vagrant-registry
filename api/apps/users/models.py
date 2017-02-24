from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token


class UserProfile(models.Model):
    BOXES_PERM_R = 'R'
    BOXES_PERM_RW = 'RW'
    BOXES_PERMS_CHOICES = (
        (BOXES_PERM_R, 'Pull'),
        (BOXES_PERM_RW, 'Pull/Push')
    )

    user = models.OneToOneField(
        'auth.User',
        related_name='profile',
        on_delete=models.CASCADE,
        primary_key=True,
    )
    boxes_permissions = models.CharField(
        max_length=2,
        choices=BOXES_PERMS_CHOICES,
        default=BOXES_PERM_RW,
    )

    def __str__(self):
        return str(self.user)


class MyToken(Token):

    class Meta:
        proxy = True
        verbose_name = 'Token'

    @property
    def expires(self):
        return self.created + timedelta(hours=settings.TOKEN_EXPIRE_AFTER)

    @property
    def is_expired(self):
        return self.expires < timezone.now()

    @property
    def is_valid(self):
        return not self.is_expired
