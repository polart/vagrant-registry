import uuid

from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from apps.boxes.utils import get_file_hash


class Box(models.Model):
    PRIVATE = 'PT'
    USERS = 'AU'
    PUBLIC = 'PC'
    VISIBILITY_CHOICES = (
        (PRIVATE, 'Private'),
        (USERS, 'All users'),
        (PUBLIC, 'Public'),
    )

    owner = models.ForeignKey('auth.User', related_name='boxes')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    visibility = models.CharField(
        max_length=2, choices=VISIBILITY_CHOICES, default=PRIVATE)
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        unique_together = ('owner', 'name')

    def __str__(self):
        return self.tag

    @property
    def tag(self):
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
    date_modified = models.DateTimeField(auto_now=True)
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
    # Vagrant currently only supports these types
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
    date_modified = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to=user_box_upload_path)
    file_size = models.BigIntegerField(default=0)
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

    @property
    def download_url(self):
        return reverse(
            'downloads-box',
            kwargs={
                'username': self.version.box.owner.username,
                'box_name': self.version.box.name,
                'version': self.version.version,
                'provider': self.provider
            }
        )


def chunked_upload_path(instance, filename):
    return 'chunked_uploads/{user}/{filename}.part'.format(
        user=instance.box.owner,
        filename=instance.id
    )


class BoxUpload(models.Model):
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
    box = models.ForeignKey('Box', related_name='uploads')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    file = models.FileField(
        max_length=255, upload_to=chunked_upload_path,
        null=True, blank=True)
    filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField(default=0)
    offset = models.BigIntegerField(default=0)
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=STARTED)
    checksum_type = models.CharField(
        max_length=10,
        choices=BoxProvider.CHECKSUM_TYPE_CHOICES)
    checksum = models.CharField(max_length=128)
    version = models.CharField(
        max_length=40,
        validators=[BoxVersion.VERSION_VALIDATOR]
    )
    provider = models.CharField(max_length=100)

    def __str__(self):
        return (
            '({self.id}) {self.box.tag} v{self.version} '
            '{self.provider}: {status}'
            .format(self=self, status=self.get_status_display())
        )

    def append_chunk(self, chunk):
        if self.file:
            # Close file opened by Django in 'rb' mode
            self.file.file.close()
            self.file.file.open(mode='ab')
            self.file.file.write(chunk.read())
            self.file.file.close()
        else:
            self.file.save(name=chunk.name, content=chunk)

        size = self.file.size
        self.offset = size
        if size == self.file_size:
            self._complete_upload()
        else:
            self.status = self.IN_PROGRESS

        self.save()
        self.file.close()

    def _complete_upload(self):
        file_hash = get_file_hash(self.file, self.checksum_type)
        assert file_hash == self.checksum, \
            "Checksum of uploaded file ({}) doesn't match " \
            "provided checksum ({}) when upload was initiated. " \
            "Checksum type is {}."\
            .format(file_hash, self.checksum,
                    self.get_checksum_type_display())

        self.status = self.COMPLETED
        self.date_completed = timezone.now()
        box_version = self._create_box_version()
        self._create_box_provider(box_version)

    def _create_box_version(self):
        return self.box.versions.get_or_create(version=self.version)[0]

    def _create_box_provider(self, box_version):
        assert not self._is_version_provider_exists(), \
            'Provider "{}" already exists for version "{}"'\
            .format(self.provider, self.version)
        box_provider = BoxProvider(
            version=box_version,
            provider=self.provider,
            checksum_type=self.checksum_type,
            checksum=self.checksum,
            file_size=self.file_size,
        )
        box_provider.file.save(name=str(self.file), content=self.file)
        box_provider.save()

    def _is_version_provider_exists(self):
        try:
            (self.box
             .versions.get(version=self.version)
             .providers.get(provider=self.provider))
            return True
        except (BoxVersion.DoesNotExist, BoxProvider.DoesNotExist):
            return False
