from django.contrib.auth.models import AnonymousUser
from django.http.response import Http404
from rest_framework.test import APITestCase, APIRequestFactory

from apps.boxes.models import Box, BoxMember
from apps.boxes.permissions import BoxPermissions
from apps.factories import StaffFactory, UserFactory, BoxFactory
from apps.users.models import UserProfile


class BoxPermissionsTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.perm = BoxPermissions()

    def check_model_perms(self, checks, user):
        for method, check in checks.items():
            request = self.factory.generic(method, '/url/')
            request.user = user
            self.assertEqual(
                self.perm.has_permission(request, 'view'),
                check,
                msg="Invalid perms for user {} and method {}"
                    .format(user, method))

    def check_obj_perms(self, checks, user, obj):
        for method, check in checks.items():
            request = self.factory.generic(method, '/url/')
            request.user = user
            fail_msg = "Invalid obj perms for user {} and method {}".format(user, method)
            if type(check) == bool:
                self.assertEqual(
                    self.perm.has_object_permission(request, 'view', obj),
                    check, msg=fail_msg)
            else:
                with self.assertRaises(check, msg=fail_msg):
                    self.perm.has_object_permission(request, 'view', obj)

    def check_box_obj_perms(self, checks, user, box_owner=None, shared_with=None):
        if box_owner is None:
            box_owner = UserFactory()
        for visibility in [Box.PRIVATE, Box.USERS, Box.PUBLIC]:
            box = BoxFactory(visibility=visibility, owner=box_owner)
            self.check_obj_perms(checks, user, box)

    def test_staff_perms(self):
        user = StaffFactory()
        checks = {
            'GET': True,
            'PATCH': True,
            'POST': True,
            'DELETE': True,
        }
        self.check_model_perms(checks, user)
        self.check_box_obj_perms(checks, user)

    def test_anonymous_model_perms(self):
        user = AnonymousUser()
        checks = {
            'GET': True,
            'PATCH': False,
            'POST': False,
            'DELETE': False,
        }
        self.check_model_perms(checks, user)

    def test_anonymous_private_box_object_perms(self):
        user = AnonymousUser()
        checks = {
            'GET': Http404,
            'PATCH': Http404,
            'POST': Http404,
            'DELETE': Http404,
        }
        box = BoxFactory(visibility=Box.PRIVATE)
        self.check_obj_perms(checks, user, box)

    def test_anonymous_users_box_object_perms(self):
        user = AnonymousUser()
        checks = {
            'GET': Http404,
            'PATCH': Http404,
            'POST': Http404,
            'DELETE': Http404,
        }
        box = BoxFactory(visibility=Box.USERS)
        self.check_obj_perms(checks, user, box)

    def test_anonymous_public_box_object_perms(self):
        user = AnonymousUser()
        checks = {
            'GET': True,
            'PATCH': False,
            'POST': False,
            'DELETE': False,
        }
        box = BoxFactory(visibility=Box.PUBLIC)
        self.check_obj_perms(checks, user, box)

    def test_box_owner_box_object_perms(self):
        user = UserFactory()
        checks = {
            'GET': True,
            'PATCH': True,
            'POST': True,
            'DELETE': True,
        }
        self.check_box_obj_perms(checks, user, box_owner=user)

    def test_authenticated_without_model_perms(self):
        user = UserFactory(profile__boxes_permissions='')
        checks = {
            'GET': False,
            'PATCH': False,
            'POST': False,
            'DELETE': False,
        }
        self.check_model_perms(checks, user)

    def test_authenticated_with_read_boxes_perms(self):
        user = UserFactory(profile__boxes_permissions=UserProfile.BOXES_READ)
        checks = {
            'GET': True,
            'PATCH': False,
            'POST': False,
            'DELETE': False,
        }
        self.check_model_perms(checks, user)

    def test_authenticated_with_read_write_boxes_perms(self):
        user = UserFactory()
        checks = {
            'GET': True,
            'PATCH': True,
            'POST': True,
            'DELETE': True,
        }
        self.check_model_perms(checks, user)

    def test_box_member_with_read_permissions(self):
        user = UserFactory()
        checks = {
            'GET': True,
            'PATCH': False,
            'POST': False,
            'DELETE': False,
        }
        box = BoxFactory(visibility=Box.PRIVATE)
        box.share_with(user, BoxMember.PERM_R)
        self.check_obj_perms(checks, user, box)

    def test_box_member_with_read_write_permissions(self):
        user = UserFactory()
        checks = {
            'GET': True,
            'PATCH': True,
            'POST': True,
            'DELETE': False,
        }
        box = BoxFactory(visibility=Box.PRIVATE)
        box.share_with(user, BoxMember.PERM_RW)
        self.check_obj_perms(checks, user, box)

    def test_authenticated_users_box_object_permissions(self):
        user = UserFactory()
        checks = {
            'GET': True,
            'PATCH': False,
            'POST': False,
            'DELETE': False,
        }
        box = BoxFactory(visibility=Box.USERS)
        self.check_obj_perms(checks, user, box)

