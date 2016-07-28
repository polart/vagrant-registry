from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIRequestFactory

from apps.factories import UserFactory
from apps.users.authentication import QueryStringBasedTokenAuthentication


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
        token = Token.objects.create(user=user)
        request = self.factory.get('/url/')
        request.query_params = {'auth_token': token.key}

        auth_user, auth_token = self.auth.authenticate(request)

        self.assertEqual(auth_user, user)
        self.assertEqual(auth_token, token)
