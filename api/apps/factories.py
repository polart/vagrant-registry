import random

import factory
import hashlib

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from apps.boxes import models
from apps.boxes.models import BoxProvider
from apps.users.models import UserProfile


User = get_user_model()


PROVIDERS = [
    'virtualbox',
    'vmware',
    'docker',
    'google',
    'aws',
    'digitalocean',
]


def get_random_provider():
    return random.choice(PROVIDERS)


def get_random_version():
    return '{}.{}.{}'.format(
        random.randint(0, 10),
        random.randint(0, 15),
        random.randint(0, 20),
    )


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'username{0}'.format(n))
    first_name = factory.Faker('first_name')
    last_name = 'User'
    email = factory.Faker('email')
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
    is_staff = True
    is_superuser = True
    last_name = 'Admin'


class StaffFactory(UserFactory):
    is_staff = True
    is_superuser = False
    last_name = 'Staff'


class BoxFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Box

    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: 'box{0}'.format(n))
    visibility = models.Box.PRIVATE
    short_description = factory.Faker('text', max_nb_chars=100)


class BoxVersionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.BoxVersion

    box = factory.SubFactory(BoxFactory)
    version = factory.LazyFunction(get_random_version)


class EmptyBoxProviderFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.BoxProvider

    version = factory.SubFactory(BoxVersionFactory)
    provider = factory.LazyFunction(get_random_provider)
    pulls = factory.Faker('random_int', min=0, max=100)
    status = models.BoxProvider.EMPTY


FILE_CONTENT = b'test'


def object_file_content(o):
    if o.file:
        o.file.seek(0)
        return o.file.read()
    else:
        return b''


class BoxProviderFactory(EmptyBoxProviderFactory):
    file = factory.django.FileField(data=FILE_CONTENT)
    file_size = factory.LazyAttribute(
        lambda o: len(object_file_content(o))
    )
    checksum = factory.LazyAttribute(
        lambda o: hashlib.sha256(object_file_content(o)).hexdigest())
    checksum_type = BoxProvider.SHA256
    status = models.BoxProvider.FILLED_IN


class BoxUploadFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.BoxUpload

    class Params:
        file_content = FILE_CONTENT

    provider = factory.SubFactory(EmptyBoxProviderFactory)
    file_size = factory.LazyAttribute(lambda o: len(o.file_content))
    checksum = factory.LazyAttribute(
        lambda o: hashlib.sha256(o.file_content).hexdigest())
    checksum_type = BoxProvider.SHA256
    offset = 0
