import factory
import hashlib
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from apps.boxes import models
from apps.boxes.models import BoxProvider
from apps.users.models import UserProfile


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'username{0}'.format(n))
    first_name = 'John'
    last_name = factory.Sequence(lambda n: 'User{0}'.format(n))
    is_staff = False
    is_superuser = False
    # We pass in 'user' to link the generated Profile to our just-generated
    # User. This will call UserProfileFactory(user=our_new_user),
    # thus skipping the SubFactory.
    profile = factory.RelatedFactory('apps.factories.UserProfileFactory', 'user')

    @classmethod
    def _generate(cls, create, attrs):
        """Override the default _generate() to disable the post-save signal."""
        from apps.users.signals import create_user_profile

        # Note: If the signal was defined with a dispatch_uid, include that in both calls.
        post_save.disconnect(dispatch_uid='create_user_profile', sender=User)
        user = super(UserFactory, cls)._generate(create, attrs)
        post_save.connect(receiver=create_user_profile,
                          dispatch_uid='create_user_profile',
                          sender=User)
        return user


class UserProfileFactory(factory.DjangoModelFactory):
    class Meta:
        model = UserProfile

    # We pass in profile=None to prevent UserFactory from creating another
    # profile (this disables the RelatedFactory)
    user = factory.SubFactory(UserFactory, profile=None)
    boxes_permissions = UserProfile.BOXES_PERM_RW


class AdminFactory(UserFactory):
    first_name = 'Admin'
    is_staff = True
    is_superuser = True


class StaffFactory(UserFactory):
    first_name = 'Staff'
    is_staff = True
    is_superuser = False


class BoxFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Box

    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: 'box{0}'.format(n))
    visibility = models.Box.PRIVATE


class BoxVersionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.BoxVersion

    box = factory.SubFactory(BoxFactory)
    version = '0.0.1'


FILE_CONTENT = b'test'


class BoxProviderFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.BoxProvider

    version = factory.SubFactory(BoxVersionFactory)
    provider = 'virtualbox'
    file = factory.django.FileField(data=FILE_CONTENT)
    checksum = factory.LazyAttribute(
        lambda o: hashlib.sha256(FILE_CONTENT).hexdigest())
    checksum_type = BoxProvider.SHA256


class BoxUploadFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.BoxUpload

    class Params:
        file_content = b'test'

    box = factory.SubFactory(BoxFactory)
    version = '1.0.0'
    provider = 'virtualbox'
    file_size = factory.LazyAttribute(lambda o: len(o.file_content))
    checksum = factory.LazyAttribute(
        lambda o: hashlib.sha256(o.file_content).hexdigest())
    checksum_type = BoxProvider.SHA256
    offset = 0
