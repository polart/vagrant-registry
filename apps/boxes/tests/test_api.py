from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from apps.boxes.api_views import FileUploadView
from apps.boxes.factories import BoxUploadFactory, BoxProviderFactory
from apps.boxes.models import BoxUpload


class FileUploadViewTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = FileUploadView.as_view()

    def get_request(self, data, content_range):
        return self.factory.put(
            '/url/', data,
            content_type='application/octet-stream',
            HTTP_CONTENT_RANGE='bytes {c[0]}-{c[1]}/{c[2]}'.format(
                c=content_range)
        )

    def get_file_length(self, file_data):
        data = file_data.encode()
        return data, len(file_data.encode())

    def get_response(self, request, bu_factory):
        return self.view(
            request,
            username=bu_factory.box.owner.username,
            box_name=bu_factory.box.name,
            pk=bu_factory.pk,
        )

    def test_unsupported_media_type(self):
        bu_factory = BoxUploadFactory()

        request = self.factory.put('/url/', data='data')
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_content_range_header_is_required(self):
        bu_factory = BoxUploadFactory()

        request = self.factory.put('/url/', 'test',
                                   content_type='application/octet-stream',)
        response = self.get_response(request, bu_factory)

        response.render()
        self.assertEqual(response.status_code,
                         status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)
        self.assertIn('Content-Range', str(response.content))

    def test_invalid_content_range_header_not_accepted(self):
        bu_factory = BoxUploadFactory()

        request = self.get_request('test', (1, 'a', None))
        response = self.get_response(request, bu_factory)

        response.render()
        self.assertEqual(response.status_code,
                         status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)
        self.assertIn('Content-Range', str(response.content))

    def test_invalid_offset_in_content_range_header_not_accepted(self):
        file_data, file_len = self.get_file_length('test content')
        bu_factory = BoxUploadFactory(file_content=file_data, offset=5)

        request = self.get_request(file_data, (2, 2 + file_len, file_len))
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code,
                         status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    def test_invalid_complete_length_in_content_range_header_not_accepted(self):
        file_data, file_len = self.get_file_length('test content')
        bu_factory = BoxUploadFactory(file_content=file_data)

        request = self.get_request(file_data, (0, file_len, file_len + 10))
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code,
                         status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    def test_invalid_last_byte_in_content_range_header_not_accepted(self):
        file_data, file_len = self.get_file_length('test content')
        bu_factory = BoxUploadFactory(file_content=file_data)

        request = self.get_request(file_data, (0, file_len + 10, file_len))
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code,
                         status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    def test_invalid_content_length_in_content_range_header_not_accepted(self):
        file_data, file_len = self.get_file_length('test content')
        bu_factory = BoxUploadFactory(file_content=file_data)

        request = self.get_request(file_data, (2, file_len, file_len))
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code,
                         status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    def test_invalid_content_not_accepted(self):
        file_data, file_len = self.get_file_length('test')
        bu_factory = BoxUploadFactory(file_content=file_data)

        request = self.get_request('poop', (0, file_len, file_len))
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_not_accepted_when_provider_already_exists(self):
        file_data, file_len = self.get_file_length('test')
        bp_factory = BoxProviderFactory()
        bu_factory = BoxUploadFactory(file_content=file_data,
                                      version=bp_factory.version.version,
                                      provider=bp_factory.provider)

        request = self.get_request(file_data, (0, file_len, file_len))
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_file_data_not_allowed(self):
        file_data, file_len = self.get_file_length('')
        bu_factory = BoxUploadFactory(file_content=file_data)

        request = self.get_request(file_data, (0, file_len, file_len))
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_box_uploaded_successfully_at_once(self):
        file_data, file_len = self.get_file_length('Ї12\n345\t6789')
        bu_factory = BoxUploadFactory(file_content=file_data)

        request = self.get_request(file_data, (0, file_len, file_len))
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED)

        box_upload = BoxUpload.objects.get(pk=bu_factory.pk)
        self.assertEqual(box_upload.file.read(), file_data)
        self.assertEqual(box_upload.status, BoxUpload.COMPLETED)
        self.assertNotEqual(box_upload.date_completed, None)
        self.assertNotEqual(box_upload.box_id, None)

        box = (box_upload.box
               .versions.get(version=bu_factory.version)
               .providers.get(provider=bu_factory.provider))
        self.assertEqual(box.file.read(), file_data)

    def test_box_uploaded_successfully_in_chunks(self):
        chunk = 'Ї12\n345\t6789\n'
        chunks_num = 5
        _, chunk_len = self.get_file_length(chunk)
        file_data, file_len = self.get_file_length(''.join([chunk]*chunks_num))
        bu_factory = BoxUploadFactory(file_content=file_data)

        for i in range(chunks_num):
            request = self.get_request(
                chunk, (chunk_len * i, chunk_len * (i + 1), file_len))
            response = self.get_response(request, bu_factory)

            if i == chunks_num - 1:
                check_status = status.HTTP_201_CREATED
            else:
                check_status = status.HTTP_202_ACCEPTED
            self.assertEqual(response.status_code, check_status)

        box_upload = BoxUpload.objects.get(pk=bu_factory.pk)
        self.assertEqual(box_upload.file.read(), file_data)
        self.assertEqual(box_upload.status, BoxUpload.COMPLETED)
        self.assertNotEqual(box_upload.date_completed, None)
        self.assertNotEqual(box_upload.box_id, None)

        box = (box_upload.box
               .versions.get(version=bu_factory.version)
               .providers.get(provider=bu_factory.provider))
        self.assertEqual(box.file.read(), file_data)

