import factory
import hashlib
from django.contrib.auth.models import User

from apps.boxes import models
from apps.boxes.models import BoxProvider


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'username{0}'.format(n))
    first_name = 'John'
    last_name = factory.Sequence(lambda n: 'User{0}'.format(n))
    is_staff = False
    is_superuser = False


class AdminFactory(UserFactory):
    first_name = 'Admin'
    is_staff = True
    is_superuser = True


class BoxFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Box

    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: 'box{0}'.format(n))


class BoxUploadFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.BoxUpload

    class Params:
        file_content = b'0123456789'

    box = factory.SubFactory(BoxFactory)
    version = '1.0.0'
    provider = 'virtualbox'
    file_size = factory.LazyAttribute(lambda o: len(o.file_content))
    checksum = factory.LazyAttribute(
        lambda o: hashlib.sha256(o.file_content).hexdigest())
    checksum_type = BoxProvider.SHA256
