import uuid

from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from guardian.models import UserObjectPermissionBase, GroupObjectPermissionBase
from guardian.shortcuts import get_user_perms

from apps.boxes.utils import get_file_hash


class BoxQuerySet(models.QuerySet):

    def private(self):
        return self.filter(visibility=Box.PRIVATE)

    def with_users(self):
        return self.filter(visibility=Box.USERS)

    def public(self):
        return self.filter(visibility=Box.PUBLIC)

    def for_user(self, user):
        if user.is_anonymous():
            return self.filter(visibility=Box.PUBLIC)
        if user.is_staff:
            # Staff has access to all boxes
            return self

        return (self
                .filter(
                    Q(boxuserobjectpermission__user=user) |
                    Q(visibility__in=[Box.PUBLIC, Box.USERS]) |
                    Q(owner=user))
                .distinct())

    def by_owner(self, user):
        return self.filter(owner=user)


class Box(models.Model):
    PRIVATE = 'PT'
    USERS = 'AU'
    PUBLIC = 'PC'
    VISIBILITY_CHOICES = (
        (PRIVATE, 'Private'),
        (USERS, 'All users'),
        (PUBLIC, 'Public'),
    )

    objects = BoxQuerySet.as_manager()

    owner = models.ForeignKey('auth.User', related_name='boxes')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    visibility = models.CharField(
        max_length=2, choices=VISIBILITY_CHOICES, default=PRIVATE)
    name = models.CharField(max_length=30)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('owner', 'name')
        permissions = (
            ('pull_box', 'Can pull box'),
            ('push_box', 'Can push box'),
        )

    def __str__(self):
        return self.tag

    @property
    def all_perms(self):
        return 'boxes.pull_box', 'boxes.push_box',

    @property
    def tag(self):
        return '{}/{}'.format(self.owner, self.name)

    def get_perms_for_user(self, user):
        is_authenticated = user and user.is_authenticated()
        is_staff = is_authenticated and user.is_staff
        is_owner = is_authenticated and self.owner == user

        if is_staff or is_owner:
            # Staff and owner have all permissions on the box
            return ['boxes.pull_box', 'boxes.push_box',
                    'boxes.update_box', 'boxes.delete_box']

        if is_authenticated:
            visibility_perms = {
                self.PUBLIC: ['boxes.pull_box'],
                self.USERS: ['boxes.pull_box'],
                self.PRIVATE: [],
            }
            user_perms = get_user_perms(user, self)
            if user_perms:
                return ['boxes.' + p for p in user_perms]
            return visibility_perms[self.visibility]

        else:
            visibility_perms = {
                self.PUBLIC: ['boxes.pull_box'],
                self.USERS: [],
                self.PRIVATE: [],
            }
            return visibility_perms[self.visibility]

    def user_has_perms(self, perms, user):
        if not perms:
            return True
        user_perms = self.get_perms_for_user(user)
        return all([p in user_perms for p in perms])

    def user_can_pull(self, user):
        return 'boxes.pull_box' in self.get_perms_for_user(user)

    def user_can_push(self, user):
        return 'boxes.push_box' in self.get_perms_for_user(user)


class BoxUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(Box)


class BoxGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(Box)


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
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('box', 'version')

    def __str__(self):
        return '{} v{}'.format(self.box, self.version)

    @property
    def owner(self):
        return self.box.owner

    @property
    def visibility(self):
        return self.box.visibility

    def user_has_perms(self, perms, user):
        return self.box.user_has_perms(perms, user)


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

    @property
    def owner(self):
        return self.version.box.owner

    @property
    def visibility(self):
        return self.version.box.visibility

    def user_has_perms(self, perms, user):
        return self.version.box.user_has_perms(perms, user)


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

    @property
    def owner(self):
        return self.box.owner

    @property
    def visibility(self):
        return self.box.visibility

    def user_has_perms(self, perms, user):
        return self.box.user_has_perms(perms, user)

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

        box_version = self._create_box_version()
        self._create_box_provider(box_version)
        self.status = self.COMPLETED
        self.date_completed = timezone.now()

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
