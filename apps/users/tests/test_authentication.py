from datetime import timedelta

from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APITestCase, APIRequestFactory

from apps.factories import UserFactory
from apps.users.authentication import QueryStringBasedTokenAuthentication, ExpiringTokenAuthentication


class QueryStringBasedTokenAuthenticationTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.auth = QueryStringBasedTokenAuthentication()

    def test_no_token_query_string(self):
        request = self.factory.get('/url/')
        request.query_params = {}

        auth = self.auth.authenticate(request)

        self.assertIsNone(auth)

    def test_token_in_query_string(self):
        user = UserFactory()
        token = user.auth_token
        request = self.factory.get('/url/')
        request.query_params = {'auth_token': token.key}

        auth_user, auth_token = self.auth.authenticate(request)

        self.assertEqual(auth_user, user)
        self.assertEqual(auth_token, token)


class ExpiringTokenAuthenticationTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.auth = ExpiringTokenAuthentication()

    def test_token_expired(self):
        user = UserFactory()
        token = user.auth_token
        token.created -= timedelta(hours=settings.TOKEN_EXPIRE_AFTER + 1)
        token.save()
        request = self.factory.get(
            '/url/',
            HTTP_AUTHORIZATION='Token {}'.format(token.key)
        )

        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_token_valid(self):
        user = UserFactory()
        token = user.auth_token
        request = self.factory.get(
            '/url/',
            HTTP_AUTHORIZATION='Token {}'.format(token.key)
        )

        auth_user, auth_token = self.auth.authenticate(request)

        self.assertEqual(auth_user, user)
        self.assertEqual(auth_token, token)
