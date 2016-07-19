from django.db import models


class UserProfile(models.Model):
    BOXES_NONE = ''
    BOXES_PERM_R = 'R'
    BOXES_PERM_RW = 'RW'
    BOXES_PERMS_CHOICES = (
        (BOXES_NONE, 'No permissions'),
        (BOXES_PERM_R, 'View/pull boxes'),
        (BOXES_PERM_RW, 'View/pull/push boxes')
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
        blank=True,
    )

    def __str__(self):
        return str(self.user)
