from django.contrib.auth.models import AnonymousUser
from django.http.response import Http404
from guardian.shortcuts import assign_perm
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from apps.boxes.factories import StaffFactory, UserFactory, BoxFactory
from apps.boxes.models import Box
from apps.boxes.permissions import UserPermissions, BoxPermissions


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

    def check_box_obj_perms(self, checks, user, box_owner=None):
        if box_owner is None:
            box_owner = UserFactory()
        for visibility in [Box.PRIVATE, Box.USERS, Box.PUBLIC]:
            box = BoxFactory(visibility=visibility, owner=box_owner)
            self.check_obj_perms(checks, user, box)

    def test_staff_has_perms(self):
        user = StaffFactory()
        checks = {
            'GET': True,
            'PATCH': True,
            'POST': True,
            'DELETE': True,
        }
        self.check_model_perms(checks, user)
        self.check_box_obj_perms(checks, user)

    def test_box_owner_doesnt_have_model_perms(self):
        user = UserFactory()
        checks = {
            'GET': False,
            'PATCH': False,
            'POST': False,
            'DELETE': False,
        }
        self.check_model_perms(checks, user)
        checks = {
            'GET': True,
            'PATCH': True,
            'POST': True,
            'DELETE': True,
        }
        self.check_box_obj_perms(checks, user, box_owner=user)

    def test_box_owner_has_read_model_perms(self):
        user = UserFactory()
        assign_perm('boxes.pull_box', user)
        checks = {
            'GET': True,
            'PATCH': False,
            'POST': False,
            'DELETE': False,
        }
        self.check_model_perms(checks, user)
        checks = {
            'GET': True,
            'PATCH': True,
            'POST': True,
            'DELETE': True,
        }
        self.check_box_obj_perms(checks, user, box_owner=user)

    def test_box_owner_has_read_write_model_perms(self):
        user = UserFactory()
        assign_perm('boxes.pull_box', user)
        assign_perm('boxes.push_box', user)
        checks = {
            'GET': True,
            'PATCH': True,
            'POST': True,
            'DELETE': True,
        }
        self.check_model_perms(checks, user)
        checks = {
            'GET': True,
            'PATCH': True,
            'POST': True,
            'DELETE': True,
        }
        self.check_box_obj_perms(checks, user, box_owner=user)


class UserPermissionsTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.perm = UserPermissions()
        self.user_obj = UserFactory()

    def check_perms(self, checks, user):
        for method, check in checks.items():
            request = self.factory.generic(method, '/url/')
            request.user = user
            self.assertEqual(
                self.perm.has_permission(request, 'view'),
                check,
                msg="Invalid perms for user {} and method {}"
                    .format(user, method))

    def check_obj_perms(self, checks, user):
        for method, check in checks.items():
            request = self.factory.generic(method, '/url/')
            request.user = user
            self.assertEqual(
                self.perm.has_object_permission(request, 'view', self.user_obj),
                check,
                msg="Invalid obj perms for user {} and method {}"
                    .format(user, method))

    def test_staff_has_perms(self):
        user = StaffFactory()
        checks = {
            'GET': True,
            'PATCH': True,
            'POST': True,
            'DELETE': True,
        }
        self.check_perms(checks, user)
        self.check_obj_perms(checks, user)

    def test_authenticated_has_perms(self):
        user = UserFactory()
        checks = {
            'GET': True,
            'PATCH': True,
            'POST': False,
            'DELETE': False,
        }
        self.check_perms(checks, user)
        checks = {
            'GET': True,
            'PATCH': False,
            'POST': False,
            'DELETE': False,
        }
        self.check_obj_perms(checks, user)

    def test_user_owner_has_perms(self):
        user = self.user_obj
        checks = {
            'GET': True,
            'PATCH': True,
            'POST': False,
            'DELETE': False,
        }
        self.check_perms(checks, user)
        checks = {
            'GET': True,
            'PATCH': True,
            'POST': False,
            'DELETE': False,
        }
        self.check_obj_perms(checks, user)

    def test_anonymous_doesnt_has_perms(self):
        user = AnonymousUser()

        request = self.factory.post('/url/')
        request.user = user
        with self.assertRaises(Http404):
            self.perm.has_permission(request, 'view')

        request = self.factory.patch('/url/')
        request.user = user
        with self.assertRaises(Http404):
            self.perm.has_permission(request, 'view')

        request = self.factory.get('/url/')
        request.user = user
        with self.assertRaises(Http404):
            self.perm.has_permission(request, 'view')
