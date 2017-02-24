from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APITestCase, APIRequestFactory

from apps.boxes.models import Box, BoxMember
from apps.boxes.serializers import BoxSerializer
from apps.factories import UserFactory, BoxFactory, StaffFactory


class BoxSerializerTestCase(APITestCase):

    def setUp(self):
        self.serializer = BoxSerializer()

    def test_get_members_by_box_owner(self):
        user1 = UserFactory()
        user2 = UserFactory()
        box = BoxFactory(owner=user1, visibility=Box.PRIVATE)
        box.share_with(user2, BoxMember.PERM_R)

        request = APIRequestFactory().get('/url/')
        request.user = user1
        self.serializer.context['request'] = request
        members = self.serializer.get_members(box)

        self.assertEqual(len(members), 1)
        self.assertEqual(members[0]['username'], user2.username)

    def test_get_members_by_staff(self):
        staff = StaffFactory()
        user2 = UserFactory()
        box = BoxFactory(visibility=Box.PRIVATE)
        box.share_with(user2, BoxMember.PERM_R)

        request = APIRequestFactory().get('/url/')
        request.user = staff
        self.serializer.context['request'] = request
        members = self.serializer.get_members(box)

        self.assertEqual(len(members), 1)
        self.assertEqual(members[0]['username'], user2.username)

    def test_get_members_by_authenticated(self):
        user1 = UserFactory()
        user2 = UserFactory()
        box = BoxFactory(visibility=Box.PRIVATE)
        box.share_with(user2, BoxMember.PERM_R)

        request = APIRequestFactory().get('/url/')
        request.user = user1
        self.serializer.context['request'] = request
        members = self.serializer.get_members(box)

        self.assertEqual(len(members), 0)

    def test_get_members_by_anonymous(self):
        user1 = AnonymousUser()
        user2 = UserFactory()
        box = BoxFactory(visibility=Box.PRIVATE)
        box.share_with(user2, BoxMember.PERM_R)

        request = APIRequestFactory().get('/url/')
        request.user = user1
        self.serializer.context['request'] = request
        members = self.serializer.get_members(box)

        self.assertEqual(len(members), 0)
