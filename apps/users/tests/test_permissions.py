from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from rest_framework.test import APITestCase, APIRequestFactory

from apps.factories import UserFactory, StaffFactory
from apps.users.permissions import UserPermissions


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