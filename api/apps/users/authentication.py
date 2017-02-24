from django.utils.translation import ugettext_lazy as _
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.users.models import MyToken


class ExpiringTokenAuthentication(TokenAuthentication):
    model = MyToken

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        if token.is_expired:
            raise AuthenticationFailed(_('Token has expired.'))

        return token.user, token


class QueryStringBasedTokenAuthentication(ExpiringTokenAuthentication):
    def authenticate(self, request):
        key = request.query_params.get('auth_token', '').strip()
        if key:
            return self.authenticate_credentials(key)
        return None
