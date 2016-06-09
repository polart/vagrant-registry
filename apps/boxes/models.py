import uuid

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
    # Validate version according to Vagrant docs
    # https://www.vagrantup.com/docs/boxes/versioning.html
    VERSION_VALIDATOR = RegexValidator(
        regex=r'^(\d+)\.(\d+)(\.(\d+))?$',
        message='Invalid version number. It must be of the format '
                'X.Y.Z where X, Y, and Z are all positive integers.'
    )

    box = models.ForeignKey('boxes.Box', related_name='versions')
    date_created = models.DateTimeField(auto_now_add=True)
    version = models.CharField(
        max_length=40, validators=[VERSION_VALIDATOR])

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


def chunked_upload_path(instance, filename):
    return 'chunked_uploads/{user}/{filename}.part'.format(
        user=instance.user,
        filename=instance.id
    )


class BoxChunkedUpload(models.Model):
    STARTED = 'S'
    IN_PROGRESS = 'I'
    COMPLETED = 'C'
    STATUS_CHOICES = (
        (STARTED, 'Started'),
        (IN_PROGRESS, 'In progress'),
        (COMPLETED, 'Completed'),
    )

    id = models.UUIDField(unique=True, default=uuid.uuid4,
                          editable=False, primary_key=True)
    user = models.ForeignKey('auth.User', related_name='box_uploads')
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    file = models.FileField(max_length=255, upload_to=chunked_upload_path)
    filename = models.CharField(max_length=255)
    offset = models.BigIntegerField(default=0)
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=STARTED)
    name = models.CharField(max_length=255)
    checksum_type = models.CharField(
        max_length=10,
        choices=BoxProvider.CHECKSUM_TYPE_CHOICES,
        default=BoxProvider.SHA256)
    checksum = models.CharField(max_length=128)
    version = models.CharField(
        max_length=40,
        validators=[BoxVersion.VERSION_VALIDATOR]
    )
    provider = models.CharField(max_length=100)

    def __str__(self):
        return (
            '({self.id}) {self.user}/{self.name} v{self.version} '
            '{self.provider}: {status}'
            .format(self=self, status=self.get_status_display())
        )
