from django.db import transaction
from rest_framework import status
from rest_framework.test import (
    APITestCase, APIRequestFactory, force_authenticate)

from apps.boxes.models import BoxUpload, Box, BoxMember, BoxProvider
from apps.factories import (
    BoxUploadFactory, BoxProviderFactory, StaffFactory, UserFactory,
    BoxFactory, BoxVersionFactory)
from vagrant_registry import urls


class BoxViewSetTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = urls.all_box_list

    def test_list_boxes(self):
        user = UserFactory()
        b1 = BoxFactory(visibility=Box.PRIVATE)
        b2 = BoxFactory(visibility=Box.PRIVATE)
        b2.share_with(user, BoxMember.PERM_R)
        b3 = BoxFactory(visibility=Box.USERS)

        request = self.factory.get('/url/')
        force_authenticate(request, user=user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # b3 and b2; b1 not shared with user
        self.assertEqual(len(response.data), 2)


class UserBoxViewSetTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view_list = urls.box_list
        self.view_detail = urls.box_detail

    def test_list_user_boxes(self):
        user = UserFactory()
        user1 = UserFactory()
        b1 = BoxFactory(visibility=Box.PRIVATE, owner=user1)
        b2 = BoxFactory(visibility=Box.PRIVATE, owner=user1)
        b2.share_with(user, BoxMember.PERM_R)
        b3 = BoxFactory(visibility=Box.USERS, owner=user1)
        b4 = BoxFactory(visibility=Box.USERS)

        request = self.factory.get('/url/')
        force_authenticate(request, user=user)
        response = self.view_list(request, username=user1.username)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # b3 and b2; b1 not shared with user; b4 different owner
        self.assertEqual(len(response.data), 2)

    def test_user_creates_own_box(self):
        user = UserFactory()

        data = {
            'name': 'testbox1',
            'description': 'some description',
            'short_description': 'Test box',
            'visibility': Box.PRIVATE,
        }
        request = self.factory.post('/url/', data=data)
        force_authenticate(request, user=user)
        response = self.view_list(request, username=user.username)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Box.objects.count(), 1)
        self.assertTrue(Box.objects.filter(**data).exists())

    def test_user_updates_own_box(self):
        user = UserFactory()

        box = BoxFactory(owner=user, visibility=Box.PRIVATE)
        data = {
            'name': 'testbox1',
            'description': 'some description',
            'short_description': 'Test box',
            'visibility': Box.PUBLIC,
        }
        request = self.factory.patch('/url/', data=data)
        force_authenticate(request, user=user)
        response = self.view_detail(request, username=user.username,
                                    box_name=box.name)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Box.objects.count(), 1)
        self.assertTrue(Box.objects.filter(**data).exists())

    def test_user_creates_box_with_the_same_name(self):
        user = UserFactory()

        box = BoxFactory(owner=user, visibility=Box.PRIVATE)
        data = {
            'name': box.name,
            'description': 'some description',
            'short_description': 'Test box',
            'visibility': Box.PUBLIC,
        }
        request = self.factory.post('/url/', data=data)
        force_authenticate(request, user=user)
        # Wrap in atomic transaction because of UNIQUER DB error
        with transaction.atomic():
            response = self.view_list(request, username=user.username)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Box.objects.count(), 1)

    def test_user_cant_create_box_for_other_user(self):
        user = UserFactory()
        user1 = UserFactory()

        data = {
            'name': 'testbox1',
            'description': 'some description',
            'short_description': 'Test box',
            'visibility': Box.PRIVATE,
        }
        request = self.factory.post('/url/', data=data)
        force_authenticate(request, user=user)
        response = self.view_list(request, username=user1.username)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Box.objects.count(), 0)


class UserBoxMemberViewSetTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view_list = urls.box_member_list
        self.view_detail = urls.box_member_detail

    def test_box_owner_can_add_box_member(self):
        user = UserFactory()
        box = BoxFactory(owner=user)
        user1 = UserFactory()

        data = {
            'permissions': BoxMember.PERM_RW,
        }
        request = self.factory.post('/url/', data=data)
        force_authenticate(request, user=user)
        response = self.view_detail(
            request,
            username=user.username,
            box_name=box.name,
            member_username=user1.username)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertListEqual(list(box.shared_with.all()), [user1])

    def test_box_owner_cannot_add_already_added_box_member(self):
        user = UserFactory()
        box = BoxFactory(owner=user)
        user1 = UserFactory()
        box.share_with(user1, BoxMember.PERM_RW)

        data = {
            'permissions': BoxMember.PERM_RW,
        }
        request = self.factory.post('/url/', data=data)
        force_authenticate(request, user=user)
        # Wrap in atomic transaction because of UNIQUER DB error
        with transaction.atomic():
            response = self.view_detail(
                request,
                username=user.username,
                box_name=box.name,
                member_username=user1.username)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(list(box.shared_with.all()), [user1])

    def test_box_owner_can_view_box_members(self):
        user = UserFactory()
        box = BoxFactory(owner=user)
        user1 = UserFactory()
        box.share_with(user1, BoxMember.PERM_RW)
        user2 = UserFactory()
        box.share_with(user2, BoxMember.PERM_R)

        request = self.factory.get('/url/')
        force_authenticate(request, user=user)
        response = self.view_list(
            request,
            username=user.username,
            box_name=box.name)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_with_permissions_cannot_add_box_member(self):
        user = UserFactory()
        box = BoxFactory()
        box.share_with(user, BoxMember.PERM_RW)
        user1 = UserFactory()

        data = {
            'permissions': BoxMember.PERM_RW,
        }
        request = self.factory.post('/url/', data=data)
        force_authenticate(request, user=user)
        response = self.view_detail(
            request,
            username=box.owner.username,
            box_name=box.name,
            member_username=user1.username)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertListEqual(list(box.shared_with.all()), [user])

    def test_user_with_permissions_cannot_read_box_members(self):
        user = UserFactory()
        box = BoxFactory()
        box.share_with(user, BoxMember.PERM_RW)

        request = self.factory.get('/url/')
        force_authenticate(request, user=user)
        response = self.view_list(
            request,
            username=box.owner.username,
            box_name=box.name)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
        self.assertListEqual(list(box.shared_with.all()), [user])


class UserBoxVersionViewSetTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view_list = urls.box_version_list
        self.view_detail = urls.box_version_detail

    def test_box_owner_can_create_version(self):
        user = UserFactory()
        box = BoxFactory(owner=user)

        data = {
            'version': '1.0.1',
            'description': 'Some description',
        }
        request = self.factory.post('/url/', data=data)
        force_authenticate(request, user=user)
        response = self.view_list(
            request,
            username=box.owner.username,
            box_name=box.name)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(box.versions.filter(**data).exists())

    def test_user_with_permissions_can_create_version(self):
        user = UserFactory()
        box = BoxFactory()
        box.share_with(user, BoxMember.PERM_RW)

        data = {
            'version': '1.0.1',
            'description': 'Some description',
        }
        request = self.factory.post('/url/', data=data)
        force_authenticate(request, user=user)
        response = self.view_list(
            request,
            username=box.owner.username,
            box_name=box.name)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(box.versions.filter(**data).exists())

    def test_user_with_permissions_can_view_versions(self):
        user = UserFactory()
        box = BoxFactory()
        box.share_with(user, BoxMember.PERM_R)
        BoxVersionFactory(box=box, version='1.0.0')
        BoxVersionFactory(box=box, version='1.0.1')

        request = self.factory.get('/url/')
        force_authenticate(request, user=user)
        response = self.view_list(
            request,
            username=box.owner.username,
            box_name=box.name)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class UserBoxProviderViewSetTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view_list = urls.box_provider_list
        self.view_detail = urls.box_provider_detail

    def test_user_with_permissions_can_view_providers(self):
        user = UserFactory()
        box = BoxFactory()
        box.share_with(user, BoxMember.PERM_R)
        version = BoxVersionFactory(box=box)
        BoxProviderFactory(version=version, provider='virtualbox')
        BoxProviderFactory(version=version, provider='vmware')

        request = self.factory.get('/url/')
        force_authenticate(request, user=user)
        response = self.view_list(
            request,
            username=box.owner.username,
            box_name=box.name,
            version=version.version)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_with_permissions_cannot_delete_provider(self):
        user = UserFactory()
        box = BoxFactory()
        box.share_with(user, BoxMember.PERM_R)
        version = BoxVersionFactory(box=box)
        provider = BoxProviderFactory(version=version)

        request = self.factory.delete('/url/')
        force_authenticate(request, user=user)
        response = self.view_detail(
            request,
            username=box.owner.username,
            box_name=box.name,
            version=version.version,
            provider=provider.provider)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserBoxMetadataViewSetTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view_detail = urls.box_metadata_detail

    def test_user_with_permissions_can_view_metadata(self):
        user = UserFactory()
        box = BoxFactory()
        box.share_with(user, BoxMember.PERM_R)
        version = BoxVersionFactory(box=box)
        BoxProviderFactory(version=version, provider='virtualbox')
        BoxProviderFactory(version=version, provider='vmware')
        BoxProviderFactory()

        request = self.factory.get('/url/')
        force_authenticate(request, user=user)
        response = self.view_detail(
            request,
            username=box.owner.username,
            box_name=box.name)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_can_view_public_box_metadata(self):
        box = BoxFactory(visibility=Box.PUBLIC)
        version = BoxVersionFactory(box=box)
        BoxProviderFactory(version=version, provider='virtualbox')
        BoxProviderFactory(version=version, provider='vmware')
        BoxProviderFactory()

        request = self.factory.get('/url/')
        response = self.view_detail(
            request,
            username=box.owner.username,
            box_name=box.name)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserBoxUploadViewSetTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view_list = urls.box_upload_list

    def test_box_owner_can_initiate_upload(self):
        user = UserFactory()
        box = BoxFactory(owner=user)

        data = {
            'file_size': 100,
            'checksum_type': BoxProvider.SHA256,
            'checksum': 'asdf',
            'version': '1.1.1',
            'provider': 'vmware',
        }
        request = self.factory.post('/url/', data=data)
        force_authenticate(request, user=user)
        response = self.view_list(
            request,
            username=box.owner.username,
            box_name=box.name)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(box.uploads.filter(**data).exists())

    def test_user_with_permissions_can_initiate_upload(self):
        user = UserFactory()
        box = BoxFactory()
        box.share_with(user, BoxMember.PERM_RW)

        data = {
            'file_size': 100,
            'checksum_type': BoxProvider.SHA256,
            'checksum': 'asdf',
            'version': '1.1.1',
            'provider': 'vmware',
        }
        request = self.factory.post('/url/', data=data)
        force_authenticate(request, user=user)
        response = self.view_list(
            request,
            username=box.owner.username,
            box_name=box.name)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(box.uploads.filter(**data).exists())

    def test_user_with_permissions_can_view_uploads(self):
        user = UserFactory()
        box = BoxFactory()
        box.share_with(user, BoxMember.PERM_R)
        BoxUploadFactory(box=box)
        BoxUploadFactory(box=box)

        request = self.factory.get('/url/')
        force_authenticate(request, user=user)
        response = self.view_list(
            request,
            username=box.owner.username,
            box_name=box.name)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_upload_cannot_be_initiated_for_existing_provider(self):
        user = UserFactory()
        box = BoxFactory(owner=user)
        box_version = BoxVersionFactory(box=box)
        box_provider = BoxProviderFactory(version=box_version)

        data = {
            'file_size': 100,
            'checksum_type': BoxProvider.SHA256,
            'checksum': 'asdf',
            'version': box_version.version,
            'provider': box_provider.provider,
        }
        request = self.factory.post('/url/', data=data)
        force_authenticate(request, user=user)
        response = self.view_list(
            request,
            username=box.owner.username,
            box_name=box.name)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserBoxUploadHandlerViewSetTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # User staff user, so there is no need to assign permissions
        cls.user = StaffFactory()

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = urls.box_upload_detail

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

    def force_auth(self, request, user):
        force_authenticate(request, user=user)

    def get_response(self, request, bu_factory):
        self.force_auth(request, bu_factory.box.owner)
        return self.view(
            request,
            username=bu_factory.box.owner.username,
            box_name=bu_factory.box.name,
            pk=bu_factory.pk,
        )

    def test_unsupported_media_type(self):
        bu_factory = BoxUploadFactory(box__owner=self.user)

        request = self.factory.put('/url/', data='data')
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_content_range_header_is_required(self):
        bu_factory = BoxUploadFactory(box__owner=self.user)

        request = self.factory.put('/url/', 'test',
                                   content_type='application/octet-stream',)
        response = self.get_response(request, bu_factory)

        response.render()
        self.assertEqual(response.status_code,
                         status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)
        self.assertIn('Content-Range', str(response.content))

    def test_invalid_content_range_header_not_accepted(self):
        bu_factory = BoxUploadFactory(box__owner=self.user)

        request = self.get_request('test', (1, 'a', None))
        response = self.get_response(request, bu_factory)

        response.render()
        self.assertEqual(response.status_code,
                         status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)
        self.assertIn('Content-Range', str(response.content))

    def test_invalid_offset_in_content_range_header_not_accepted(self):
        file_data, file_len = self.get_file_length('test content')
        bu_factory = BoxUploadFactory(box__owner=self.user,
                                      file_content=file_data, offset=5)

        request = self.get_request(file_data, (2, 2 + file_len, file_len))
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code,
                         status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    def test_invalid_complete_length_in_content_range_header_not_accepted(self):
        file_data, file_len = self.get_file_length('test content')
        bu_factory = BoxUploadFactory(box__owner=self.user,
                                      file_content=file_data)

        request = self.get_request(file_data, (0, file_len, file_len + 10))
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code,
                         status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    def test_invalid_last_byte_in_content_range_header_not_accepted(self):
        file_data, file_len = self.get_file_length('test content')
        bu_factory = BoxUploadFactory(box__owner=self.user,
                                      file_content=file_data)

        request = self.get_request(file_data, (0, file_len + 10, file_len))
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code,
                         status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    def test_invalid_content_length_in_content_range_header_not_accepted(self):
        file_data, file_len = self.get_file_length('test content')
        bu_factory = BoxUploadFactory(offset=2,
                                      box__owner=self.user,
                                      file_content=file_data)

        request = self.get_request(file_data, (2, file_len, file_len))
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code,
                         status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    def test_invalid_content_not_accepted(self):
        file_data, file_len = self.get_file_length('test')
        bu_factory = BoxUploadFactory(box__owner=self.user,
                                      file_content=file_data)

        request = self.get_request('poop', (0, file_len, file_len))
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_not_accepted_when_provider_already_exists(self):
        file_data, file_len = self.get_file_length('test')
        bp_factory = BoxProviderFactory(version__box__owner=self.user)
        bu_factory = BoxUploadFactory(box=bp_factory.version.box,
                                      file_content=file_data,
                                      version=bp_factory.version.version,
                                      provider=bp_factory.provider)

        request = self.get_request(file_data, (0, file_len, file_len))
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_file_data_not_allowed(self):
        file_data, file_len = self.get_file_length('')
        bu_factory = BoxUploadFactory(box__owner=self.user,
                                      file_content=file_data)

        request = self.get_request(file_data, (0, file_len, file_len))
        response = self.get_response(request, bu_factory)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_box_uploaded_successfully_at_once(self):
        file_data, file_len = self.get_file_length('Ї12\n345\t6789')
        bu_factory = BoxUploadFactory(box__owner=self.user,
                                      file_content=file_data)

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
        bu_factory = BoxUploadFactory(box__owner=self.user,
                                      file_content=file_data)

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

