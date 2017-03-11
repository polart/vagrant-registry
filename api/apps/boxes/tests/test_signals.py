from django.test import TestCase

from apps.boxes.models import Box, BoxVersion
from apps.factories import BoxFactory, BoxVersionFactory, BoxProviderFactory


class BoxVersionDateUpdatedHandlerTestCase(TestCase):

    def test_box_date_updated(self):
        """Ensures box's `date_updated` changes with new version"""
        box = BoxFactory()
        version = BoxVersionFactory(box=box)

        updated_box = Box.objects.get(pk=box.pk)
        self.assertEqual(updated_box.date_updated, version.date_updated)


class BoxProviderDateUpdatedHandlerTestCase(TestCase):

    def test_box_date_updated(self):
        """Ensures box's and version's `date_updated` changes with new provider"""
        box = BoxFactory()
        version = BoxVersionFactory(box=box)
        provider = BoxProviderFactory(version=version)

        updated_version = BoxVersion.objects.get(pk=version.pk)
        updated_box = Box.objects.get(pk=box.pk)
        self.assertEqual(updated_version.date_updated, provider.date_updated)
        self.assertEqual(updated_box.date_updated, provider.date_updated)
