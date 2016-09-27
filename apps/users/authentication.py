from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed


class ExpiringTokenAuthentication(TokenAuthentication):
    model = Token

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        limit = timezone.now() - timedelta(hours=settings.TOKEN_EXPIRE_AFTER)
        if token.created < limit:
            raise AuthenticationFailed(_('Token has expired.'))

        return token.user, token


class QueryStringBasedTokenAuthentication(ExpiringTokenAuthentication):
    def authenticate(self, request):
        key = request.query_params.get('auth_token', '').strip()
        if key:
            return self.authenticate_credentials(key)
        return None
