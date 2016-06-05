from django.core.validators import RegexValidator
from django.db import models


class Box(models.Model):
    owner = models.ForeignKey('auth.User', related_name='boxes')
    date_created = models.DateTimeField(auto_now_add=True)
    private = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        unique_together = ('owner', 'name')

    def __str__(self):
        return '{}/{}'.format(self.owner, self.name)


class BoxVersion(models.Model):
    box = models.ForeignKey('boxes.Box', related_name='versions')
    date_created = models.DateTimeField(auto_now_add=True)
    # Validate version according to Vagrant docs
    # https://www.vagrantup.com/docs/boxes/versioning.html
    version = models.CharField(
        max_length=40,
        validators=[RegexValidator(
            regex=r'^(\d+)\.(\d+)(\.(\d+))?$',
            message='Invalid version number. It must be of the format '
                    'X.Y.Z where X, Y, and Z are all positive integers.'
        )]
    )

    class Meta:
        unique_together = ('box', 'version')

    def __str__(self):
        return '{} v{}'.format(self.box, self.version)


def user_box_upload_path(instance, filename):
    return (
        'boxes/{owner}/{box_name}/{version}/'
        '{box_name}_{version}_{provider}.box'.format(
            owner=instance.version.box.owner,
            box_name=instance.version.box.name,
            version=instance.version.version.replace('.', ''),
            provider=instance.provider)
    )


class BoxProvider(models.Model):
    # Vagrant currently only supports these  types
    # https://www.vagrantup.com/docs/vagrantfile/machine_settings.html
    MD5 = 'md5'
    SHA1 = 'sha1'
    SHA256 = 'sha256'
    CHECKSUM_TYPE_CHOICES = (
        (MD5, 'md5'),
        (SHA1, 'sha1'),
        (SHA256, 'sha256'),
    )

    version = models.ForeignKey('boxes.BoxVersion', related_name='providers')
    provider = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=user_box_upload_path)
    checksum_type = models.CharField(
        max_length=10,
        choices=CHECKSUM_TYPE_CHOICES,
        default=SHA256)
    checksum = models.CharField(max_length=128)
    description = models.TextField()

    class Meta:
        unique_together = ('version', 'provider')

    def __str__(self):
        return '{} {}'.format(self.version, self.provider)
