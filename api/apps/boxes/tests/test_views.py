from rest_framework import status
from rest_framework.test import (
    APITestCase, APIRequestFactory, force_authenticate)

from apps.boxes.models import BoxProvider
from apps.boxes.views import DownloadBoxView
from apps.factories import (
    BoxProviderFactory)


class DownloadBoxViewTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = DownloadBoxView.as_view({'get': 'get'})

    def test_on_download_only_number_of_pulls_changes(self):
        provider = BoxProviderFactory()

        request = self.factory.get('/url/')
        force_authenticate(request, user=provider.owner)
        response = self.view(
            request,
            username=provider.owner.username,
            box_name=provider.box.name,
            version=provider.version.version,
            provider=provider.provider)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_provider = BoxProvider.objects.get(pk=provider.pk)
        self.assertEqual(provider.pulls + 1, updated_provider.pulls)
        self.assertEqual(provider.date_modified, updated_provider.date_modified)
