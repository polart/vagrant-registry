from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token


# Usage of these usernames is restricted because they would interfere
# with site specific URLs when used in boxes short URLs:
# https://example.com/<username>/<box_name>/
RESTRICTED_USERNAMES = [
    'static',
    'static-api',
    'media',
    'admin',
    'box-metadata',
    'downloads',
    'api',
    'me',
]


def restrict_username_validator(value):
    if value in RESTRICTED_USERNAMES:
        raise ValidationError('Username "{}" not allowed.'.format(value))


class User(AbstractUser):

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        ),
        validators=[
            UnicodeUsernameValidator(),
            restrict_username_validator,
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['username']


class UserProfile(models.Model):
    BOXES_PERM_R = 'R'
    BOXES_PERM_RW = 'RW'
    BOXES_PERMS_CHOICES = (
        (BOXES_PERM_R, 'Pull'),
        (BOXES_PERM_RW, 'Pull/Push')
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
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
