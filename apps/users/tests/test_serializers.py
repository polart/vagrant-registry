from rest_framework.test import APITestCase, APIRequestFactory

from apps.boxes.models import Box
from apps.factories import UserFactory, BoxFactory
from apps.users.models import UserProfile
from apps.users.serializers import UserSerializer


class UserSerializerTestCase(APITestCase):

    def setUp(self):
        self.serializer = UserSerializer()

    def test_user_created(self):
        data = {
            'username': 'testuser',
            'email': 'test@email.com',
            'password': 'pass',
            'profile': {
                'boxes_permissions': UserProfile.BOXES_PERM_R,
            }
        }
        user = self.serializer.create(data)
        self.assertEqual(user.username, data['username'])
        self.assertEqual(user.email, data['email'])
        self.assertTrue(user.check_password(data['password']))
        self.assertEqual(user.profile.boxes_permissions,
                         data['profile']['boxes_permissions'])

    def test_user_updated(self):
        user = UserFactory()
        data = {
            'username': 'testuser',
            'email': 'test@email.com',
            'password': 'pass',
            'profile': {
                'boxes_permissions': UserProfile.BOXES_PERM_R,
            }
        }
        user = self.serializer.update(user, data)
        self.assertEqual(user.username, data['username'])
        self.assertEqual(user.email, data['email'])
        self.assertTrue(user.check_password(data['password']))
        self.assertEqual(user.profile.boxes_permissions,
                         data['profile']['boxes_permissions'])

    def test_get_boxes(self):
        user1 = UserFactory()
        user2 = UserFactory()
        b1 = BoxFactory(owner=user1, visibility=Box.PRIVATE)
        b2 = BoxFactory(owner=user1, visibility=Box.PUBLIC)

        request = APIRequestFactory().get('/url/')
        request.user = user2
        self.serializer.context['request'] = request
        boxes = self.serializer.get_boxes(user1)

        self.assertEqual(len(boxes), 1, msg="Private box shouldn't be shown")
        self.assertIn(b2.name, boxes[0])
        self.assertIn('http://', boxes[0], msg="Should be absolute URL")
