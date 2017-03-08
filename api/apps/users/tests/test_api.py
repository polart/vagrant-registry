from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework import status
from apps.boxes.models import Box
from apps.factories import StaffFactory, UserFactory, BoxFactory
from apps.users.api_views import UserViewSet
from apps.users.models import UserProfile


class UserViewSetTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.staff = StaffFactory()
        cls.user1 = UserFactory()

        cls.box1 = BoxFactory(owner=cls.user1, visibility=Box.PRIVATE)
        cls.box2 = BoxFactory(owner=cls.user1, visibility=Box.PUBLIC)

    def setUp(self):
        self.factory = APIRequestFactory()
        self.list_view = UserViewSet.as_view({
            'get': 'list',
            'post': 'create',
        })
        self.detail_view = UserViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        })

    def test_list_users_for_anonymous(self):
        request = self.factory.get('/url/')
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_users_for_authenticated(self):
        request = self.factory.get('/url/')
        force_authenticate(request, user=self.user1)
        response = self.list_view(request)

        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['count'], 2)
        self.assertNotIn('boxes_permissions', data['results'][0])

    def test_list_users_for_staff(self):
        request = self.factory.get('/url/')
        force_authenticate(request, user=self.staff)
        response = self.list_view(request)

        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['count'], 2)
        self.assertIn('boxes_permissions', data['results'][0])

    def test_create_new_user(self):
        data = {
            'username': 'testuser',
            'email': 'test@email.com',
            'password': 'pass',
            'boxes_permissions': UserProfile.BOXES_PERM_R,
        }
        request = self.factory.post('/url/', data)
        force_authenticate(request, user=self.staff)

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
