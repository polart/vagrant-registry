from rest_framework.authentication import TokenAuthentication


class QueryStringBasedTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        key = request.query_params.get('auth_token', '').strip()
        if key:
            return self.authenticate_credentials(key)
        return None
